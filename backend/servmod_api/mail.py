"""Pluggable mailer: MAIL_MODE=log|resend|smtp."""
import os, smtplib, ssl, logging, httpx
from email.message import EmailMessage

log = logging.getLogger("servmod.mail")
OUTBOX = []  # used by tests / log mode

def send(to: str, subject: str, text: str, reply_to: str | None = None) -> bool:
    mode = os.environ.get("MAIL_MODE", "log")
    sender = os.environ.get("MAIL_FROM", "ServMod <no-reply@servmod.com>")
    try:
        if mode == "resend":
            body = {"from": sender, "to": [to], "subject": subject, "text": text}
            if reply_to: body["reply_to"] = reply_to
            r = httpx.post("https://api.resend.com/emails", json=body, timeout=15,
                           headers={"Authorization": "Bearer " + os.environ["RESEND_API_KEY"]})
            r.raise_for_status()
        elif mode == "smtp":
            m = EmailMessage(); m["From"] = sender; m["To"] = to; m["Subject"] = subject
            if reply_to: m["Reply-To"] = reply_to
            m.set_content(text)
            with smtplib.SMTP(os.environ["SMTP_HOST"], int(os.environ.get("SMTP_PORT", "587")), timeout=15) as s:
                s.starttls(context=ssl.create_default_context())
                s.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"]); s.send_message(m)
        else:
            OUTBOX.append((to, subject, text)); log.warning("MAIL(log) to=%s subject=%s", to, subject)
        return True
    except Exception as e:
        log.error("mail failed: %s", e); return False
