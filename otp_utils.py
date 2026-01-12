import smtplib, ssl, hmac, hashlib, secrets
from smtplib import SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected, SMTPDataError, SMTPRecipientsRefused
from socket import gaierror, timeout
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from flask import current_app, render_template

POINTS_PER_VOUCHER = 500  # keep in sync with your UI

from datetime import datetime
from flask import current_app, render_template

def send_voucher_success_email(to_email: str, user_name: str):
    """Send the final voucher email (static link + PIN for your demo)."""
    html = render_template(
        "emails/voucher_email.html",
        app_name=current_app.config["APP_NAME"],
        user_name=user_name,
        current_year=datetime.now().year,
    )
    # uses the existing private helper in otp_utils
    _send_email_html(
        to_email,
        f"Your {current_app.config['APP_NAME']} E‑Voucher",
        html
    )


def _smtp_send(msg, to_email: str):
    host = current_app.config.get("SMTP_HOST")
    port = int(current_app.config.get("SMTP_PORT", 465))
    user = current_app.config.get("SMTP_USERNAME")
    pwd  = current_app.config.get("SMTP_PASSWORD")

    try:
        if port == 465:
            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=20) as s:
                if user and pwd:
                    s.login(user, pwd)
                s.sendmail(current_app.config["SMTP_SENDER"], [to_email], msg.as_string())
        else:
            # assume STARTTLS (e.g., port 587)
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.ehlo()
                s.starttls(context=ssl.create_default_context())
                s.ehlo()
                if user and pwd:
                    s.login(user, pwd)
                s.sendmail(current_app.config["SMTP_SENDER"], [to_email], msg.as_string())
    except (SMTPAuthenticationError, SMTPConnectError, SMTPServerDisconnected,
            SMTPDataError, SMTPRecipientsRefused, gaierror, timeout) as e:
        # re-raise with class name and message so the route can return it temporarily
        raise RuntimeError(f"{e.__class__.__name__}: {e}") from e

def _now_utc_naive():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def _sha256_bytes(code: str) -> bytes:
    secret = current_app.config.get("SECRET_KEY", "change-me")
    return hashlib.sha256(hmac.new(secret.encode(), code.encode(), hashlib.sha256).digest()).digest()

def _send_email_html(to_email: str, subject: str, html: str):
    msg = MIMEMultipart('alternative')
    msg['From'] = current_app.config["SMTP_SENDER"]
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html', 'utf-8'))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(current_app.config["SMTP_HOST"], int(current_app.config["SMTP_PORT"]), context=ctx) as s:
        user = current_app.config.get("SMTP_USERNAME")
        pwd  = current_app.config.get("SMTP_PASSWORD")
        if user and pwd:
            s.login(user, pwd)
        s.sendmail(current_app.config["SMTP_SENDER"], [to_email], msg.as_string())

def user_points(cursor, email: str) -> int:
    cursor.execute("SELECT points FROM User WHERE login_email=%s", (email,))
    row = cursor.fetchone()
    return int(row[0]) if row and row[0] is not None else 0

def update_user_points(db, cursor, email: str, new_points: int):
    cursor.execute("UPDATE User SET points=%s WHERE login_email=%s", (new_points, email))
    db.commit()

def upsert_otp(db, cursor, email: str, qty: int, total_points: int) -> str:
    code = f"{secrets.randbelow(1_000_000):06d}"
    code_hash = _sha256_bytes(code)
    expires_at = _now_utc_naive() + timedelta(minutes=current_app.config["OTP_TTL_MINUTES"])

    cursor.execute("DELETE FROM otp_verifications WHERE user_email=%s AND purpose='voucher'", (email,))
    db.commit()

    cursor.execute("""
      INSERT INTO otp_verifications (user_email, purpose, code_hash, expires_at, attempts, last_sent_at, qty, total_points)
      VALUES (%s, 'voucher', %s, %s, 0, %s, %s, %s)
    """, (email, code_hash, expires_at, _now_utc_naive(), qty, total_points))
    db.commit()
    return code

def can_resend(cursor, email: str) -> bool:
    cursor.execute("""
      SELECT last_sent_at FROM otp_verifications
      WHERE user_email=%s AND purpose='voucher'
      ORDER BY rewardotp_id DESC LIMIT 1
    """, (email,))
    row = cursor.fetchone()
    if not row or not row[0]:
        return True
    return (_now_utc_naive() - row[0]).total_seconds() >= current_app.config["OTP_RESEND_COOLDOWN_SECONDS"]

def get_active_otp(cursor, email: str):
    cursor.execute("""
      SELECT rewardotp_id, code_hash, expires_at, attempts, qty, total_points
      FROM otp_verifications
      WHERE user_email=%s AND purpose='voucher'
      ORDER BY rewardotp_id DESC LIMIT 1
    """, (email,))
    return cursor.fetchone()


def send_voucher_otp_email(to_email: str, code: str, qty: int, total_points: int):
    # Ensure absolute URLs for images in email (logo, icons)
    # In your template use: {{ url_for('static', filename='img/logo.png', _external=True) }}
    html = render_template(
        "emails/otp_email.html",
        app_name=current_app.config["APP_NAME"],
        code=code,
        ttl_minutes=current_app.config["OTP_TTL_MINUTES"],
        qty=qty,
        total_points=total_points,
        current_year=datetime.utcnow().year
    )

    # Plain-text fallback (helps deliverability)
    text = (
        f"{current_app.config['APP_NAME']} Voucher One-time PIN\n\n"
        f"Your code: {code}\n"
        f"Expires in: {current_app.config['OTP_TTL_MINUTES']} minutes\n"
        f"Requested: {qty} voucher(s) • {total_points} points\n\n"
        "Never share this code with anyone."
    )

    msg = MIMEMultipart('alternative')
    msg['From'] = current_app.config["SMTP_SENDER"]
    msg['To']   = to_email
    msg['Subject'] = f"{current_app.config['APP_NAME']} voucher one-time PIN"

    msg.attach(MIMEText(text, 'plain', 'utf-8'))
    msg.attach(MIMEText(html, 'html',  'utf-8'))

    _smtp_send(msg, to_email)

