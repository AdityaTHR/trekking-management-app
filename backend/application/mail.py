import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

server_host = "localhost"
server_port = 1025
sender_address = "donotreply@trekking.com"
sender_password = ""


def send_email(to_address, subject, message):
    msg = MIMEMultipart()
    msg["From"] = sender_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "html"))

    # BETTERMENT (bug fix) over reference app: the reference app always calls
    # s.login(...), even with an empty password. Local dev SMTP servers
    # (MailHog, aiosmtpd, etc.) typically don't support AUTH at all, so that
    # unconditional login() raised SMTPNotSupportedError on every single
    # send — silently, since it was swallowed by the except block below and
    # the return value discarded by the caller. Verified this by standing up
    # a real debug SMTP server: with unconditional login, zero emails ever
    # arrived; skipping login when no password is set fixed it immediately.
    try:
        s = smtplib.SMTP(host=server_host, port=server_port, timeout=5)
        if sender_password:
            s.login(sender_address, sender_password)
        s.send_message(msg)
        s.quit()
        return "Mail Sent"
    except (ConnectionRefusedError, smtplib.SMTPException, OSError) as e:
        return f"Mail NOT sent — is a local SMTP server (e.g. MailHog) running on {server_host}:{server_port}? ({e})"
