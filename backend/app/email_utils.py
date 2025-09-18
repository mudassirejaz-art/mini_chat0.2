# app/email_utils.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def send_verification_email(to_email: str, user_name: str, token: str):
    # Link points directly to login page with token
    verification_link = f"http://localhost:3000/login?token={token}"

    subject = "Verify your email - MiniChat0.2"

    html_content = f"""
    <div style="font-family: 'Inter', sans-serif; background-color: #f8fafc; padding: 60px 20px;">
      <div style="max-width: 500px; margin: 0 auto; background-color: #fff; border-radius: 16px; padding: 40px 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.08); border: 1px solid #e5e7eb;">
        <h1 style="color: #111827; font-size: 26px; font-weight: 700; margin-bottom: 12px;">Hey {user_name}, verify your email!</h1>
        <p style="color: #4b5563; font-size: 16px; margin-bottom: 32px;">
          Welcome to <strong>MiniChat0.2</strong>! Please confirm your email to activate your account.
        </p>
        <a href="{verification_link}" style="display:inline-block;padding:14px 36px;background-color:#6366f1;color:#fff;border-radius:12px;text-decoration:none;font-weight:600;font-size:16px;">Verify My Email</a>
        <p style="color:#6b7280;font-size:13px;margin-top:16px;line-height:1.5;">
          If the button doesn’t work, copy and paste this link into your browser:<br/>
          <a href="{verification_link}" style="color:#6366f1; word-break: break-all;">{verification_link}</a>
        </p>
        <p style="color:#6b7280;font-size:14px;margin-top:32px;line-height:1.5;">
          If you didn’t request this, you can safely ignore this email.
        </p>
      </div>
    </div>
    """


    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"[INFO] Verification email sent to {to_email}")

    except Exception as e:
        print(f"[ERROR] Could not send email: {e}")
