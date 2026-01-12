import secrets, hashlib
from datetime import datetime
from Database import mycursor, db 

_BACKUP_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

def _random_backup_code(length: int = 10) -> str:
    return "".join(secrets.choice(_BACKUP_ALPHABET) for _ in range(length))

def _hash_code(code: str, salt: bytes) -> bytes:
    h = hashlib.sha256()
    h.update(salt)
    h.update(code.encode("utf-8"))
    return h.digest()

def generate_2fa_backup_codes(user_email: str, count: int = 10, length: int = 10):
    mycursor.execute(
        "DELETE FROM twofa_backup_codes WHERE user_email = %s AND used_at IS NULL",
        (user_email,)
    )

    plaintext_codes, rows, seen = [], [], set()
    for _ in range(count):
        code = _random_backup_code(length)
        while code in seen:
            code = _random_backup_code(length)
        seen.add(code)
        plaintext_codes.append(code)

        salt = secrets.token_bytes(16)
        code_hash = _hash_code(code, salt)
        rows.append((user_email, code_hash, salt))

    mycursor.executemany(
        "INSERT INTO twofa_backup_codes (user_email, code_hash, salt) VALUES (%s, %s, %s)",
        rows
    )
    db.commit()
    return plaintext_codes

def verify_and_consume_backup_code(user_email: str, supplied_code: str) -> bool:
    mycursor.execute(
        "SELECT backup_id, code_hash, salt FROM twofa_backup_codes WHERE user_email = %s AND used_at IS NULL",
        (user_email,)
    )
    rows = mycursor.fetchall()
    if not rows:
        return False

    for code_id, code_hash_db, salt in rows:
        if _hash_code(supplied_code, salt) == code_hash_db:
            mycursor.execute(
                "UPDATE twofa_backup_codes SET used_at = NOW() WHERE backup_id = %s",
                (code_id,)
            )
            db.commit()
            return True
    return False

def rotate_2fa_backup_codes(user_email: str, count: int = 10, length: int = 10):
    mycursor.execute(
        "UPDATE twofa_backup_codes SET used_at = NOW() WHERE user_email = %s AND used_at IS NULL",
        (user_email,)
    )
    db.commit()
    return generate_2fa_backup_codes(user_email, count=count, length=length)
