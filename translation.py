#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
translation.py

Scan only templates/**/*.html, extract user-facing strings,
write nested JSON catalogs like:
{
  "borrow_free": { "search-for-item.ab12cd34": "Search for item", ... },
  "donate": { ... }
}

Then translate to zh (Chinese) and id (Indonesian) using DeepL.

Usage (PowerShell/CMD/Linux/mac):
  set/ export DEEPL_API_KEY=your_key
  python translation.py
Options:
  --root .                (default: .)
  --out translations      (default)
  --overwrite             (rebuild en.json from scratch instead of merging)
  --dry-run               (skip DeepL; only writes en.json)
"""

import os
import re
import json
import glob
import hashlib
import argparse
from pathlib import Path
from collections import defaultdict
from html import unescape

import requests

from dotenv import load_dotenv

load_dotenv()

# ----------------------------- Defaults -----------------------------
DEEPL_URL = "https://api-free.deepl.com/v2/translate"  # change to https://api.deepl.com/v2/translate for paid plan
TARGETS = {"zh": "ZH", "id": "ID"}  # Chinese, Indonesian

ROOT_DEFAULT = "."
OUT_DEFAULT = "translations"

INCLUDE_GLOBS = ["templates/**/*.html"]
EXCLUDE_GLOBS = ["translations/**", "static/**", "__pycache__/**", ".venv/**", "venv/**", ".git/**"]

# ----------------------------- Regex helpers -----------------------------
JINJA_PATTERN = re.compile(r"{{.*?}}|{%.+?%}", re.DOTALL)
TAG_PATTERN = re.compile(r"<[^>]+>")
SCRIPT_STYLE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
HAS_LETTERS = re.compile(r"[A-Za-z]")
WS_ONLY = re.compile(r"^\s*$")
MANY_SYMBOLS = re.compile(r"^[\W_]+$")
LIKELY_NOT_TEXT = re.compile(r"^(/|\.{1,2}/|[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)")

def sha8(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]

def slug(s: str, max_words=6):
    s = re.sub(r"\s+", " ", s).strip()
    words = s.split(" ")[:max_words]
    head = "-".join(w.lower() for w in words)
    head = re.sub(r"[^a-z0-9\-]+", "", head)
    return head or "text"

def protect_jinja(text: str):
    placeholders = {}
    def repl(m):
        key = f"__JINJA_{len(placeholders)}__"
        placeholders[key] = m.group(0)
        return key
    return JINJA_PATTERN.sub(repl, text), placeholders

def unprotect_jinja(text: str, placeholders: dict):
    for k, v in placeholders.items():
        text = text.replace(k, v)
    return text

def looks_translatable(s: str) -> bool:
    if not s or WS_ONLY.match(s): return False
    # remove script/style blocks
    s = SCRIPT_STYLE.sub("", s)
    if JINJA_PATTERN.fullmatch(s or ""): return False
    txt = TAG_PATTERN.sub("", s).strip()
    if not txt: return False
    if MANY_SYMBOLS.match(txt): return False
    if not HAS_LETTERS.search(txt): return False
    if LIKELY_NOT_TEXT.match(txt): return False
    return True

def gather_files(root: Path):
    paths = set()
    for pat in INCLUDE_GLOBS:
        for p in glob.iglob(str(root / pat), recursive=True):
            paths.add(Path(p))
    # filter excludes
    excludes = set()
    for pat in EXCLUDE_GLOBS:
        for p in glob.iglob(str(root / pat), recursive=True):
            excludes.add(Path(p))
    return [p for p in sorted(paths) if not any(str(p).startswith(str(e)) for e in excludes)]

def extract_html(path: Path):
    raw = path.read_text(encoding="utf-8", errors="ignore")
    # strip script/style
    raw = SCRIPT_STYLE.sub("", raw)
    # split by tags to get text-ish nodes
    chunks = re.split(r"<[^>]+>", raw)
    out = []
    for ch in chunks:
        text = unescape(ch).strip()
        if looks_translatable(text):
            out.append(text)
    return out

def nested_merge(dst: dict, src: dict):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            nested_merge(dst[k], v)
        else:
            dst[k] = v

def batch_translate(texts, target_lang_code, deepl_key):
    if not texts: return []
    protected = []
    placeholders_list = []
    for t in texts:
        p, ph = protect_jinja(t)
        protected.append(p)
        placeholders_list.append(ph)

    # DeepL accepts multiple 'text' fields
    data = [("text", p) for p in protected]
    data += [
        ("target_lang", target_lang_code),
        ("source_lang", "EN"),
        ("preserve_formatting", "1"),
        ("split_sentences", "nonewlines"),
    ]

    headers = {"Authorization": f"DeepL-Auth-Key {deepl_key}"}
    resp = requests.post(DEEPL_URL, data=data, headers=headers, timeout=60)
    resp.raise_for_status()
    translations = resp.json().get("translations", [])
    if len(translations) != len(texts):
        raise RuntimeError(f"DeepL returned {len(translations)} items for {len(texts)} inputs.")

    restored = []
    for i, tr in enumerate(translations):
        txt = tr.get("text", "")
        restored.append(unprotect_jinja(txt, placeholders_list[i]))
    return restored

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    deepl_key = os.getenv("DEEPL_API_KEY")
    if not deepl_key and not args.dry_run:
        raise SystemExit("DEEPL_API_KEY not set. Set env var or use --dry-run.")

    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    files = gather_files(root)
    print(f"[i18n] Scanning {len(files)} HTML files under templates/")

    # Build nested EN structure: {section: {key: text}}
    en_nested = defaultdict(dict)  # section -> {key: english}
    for f in files:
        section = f.stem  # e.g. borrow_free.html -> "borrow_free"
        texts = extract_html(f)
        for txt in texts:
            key = f"{slug(txt)}.{sha8(txt)}"  # stable, readable
            en_nested[section].setdefault(key, txt)

    en_path = out_dir / "en.json"
    if en_path.exists() and not args.overwrite:
        with en_path.open("r", encoding="utf-8") as rf:
            existing = json.load(rf)
    else:
        existing = {}

    # Merge: keep any manual edits, add new strings
    merged_en = {}
    nested_merge(merged_en, existing)
    nested_merge(merged_en, en_nested)

    # Write EN
    with en_path.open("w", encoding="utf-8") as wf:
        json.dump(merged_en, wf, ensure_ascii=False, indent=2)
    print(f"[i18n] Wrote {en_path}")

    # Prepare a stable, ordered list of (section, key, english)
    items = []
    for section in sorted(merged_en.keys()):
        inner = merged_en[section] or {}
        for key in sorted(inner.keys()):
            items.append((section, key, inner[key]))

    if args.dry_run:
        print("[i18n] Dry-run: skipped DeepL.")
        return

    # Load cache to avoid re-translation of same English
    cache_path = out_dir / ".deepl_cache.json"
    cache = {}
    if cache_path.exists():
        try:
            cache = json.load(cache_path.open("r", encoding="utf-8"))
        except Exception:
            cache = {}

    for lang, deepl_code in TARGETS.items():
        out_path = out_dir / f"{lang}.json"
        if out_path.exists() and not args.overwrite:
            with out_path.open("r", encoding="utf-8") as rf:
                tgt_nested = json.load(rf)
        else:
            tgt_nested = {}

        # Build list to translate
        to_translate_indices = []
        to_translate_texts = []
        for i, (section, key, eng) in enumerate(items):
            # ensure section exists
            tgt_nested.setdefault(section, {})
            if key in tgt_nested[section]:
                continue
            ckey = f"{eng}|{deepl_code}"
            if ckey in cache:
                tgt_nested[section][key] = cache[ckey]
            else:
                to_translate_indices.append(i)
                to_translate_texts.append(eng)

        # Batch translate
        BATCH = 40
        for j in range(0, len(to_translate_texts), BATCH):
            batch = to_translate_texts[j:j+BATCH]
            translated = batch_translate(batch, deepl_code, deepl_key)
            for k, tr in enumerate(translated):
                i = to_translate_indices[j + k]
                section, key, eng = items[i]
                tgt_nested[section][key] = tr
                cache[f"{eng}|{deepl_code}"] = tr

        with out_path.open("w", encoding="utf-8") as wf:
            json.dump(tgt_nested, wf, ensure_ascii=False, indent=2)
        print(f"[i18n] Wrote {out_path}")

    with cache_path.open("w", encoding="utf-8") as wf:
        json.dump(cache, wf, ensure_ascii=False, indent=2)

    print("[i18n] Done. JSONs are nested by page/section (template filename).")
    print("       Rename keys in en.json to semantic ones (e.g. 'title', 'search_placeholder') anytime;")
    print("       rerun with --overwrite to propagate structure to zh/id.")

if __name__ == "__main__":
    main()
