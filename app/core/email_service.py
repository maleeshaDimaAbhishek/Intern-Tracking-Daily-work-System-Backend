import smtplib
import os
from pathlib import Path
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# ── Configure these ──────────────────────────────────────────
SMTP_EMAIL    = os.getenv("SMTP_EMAIL")   # ← your Gmail
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")      # ← Gmail App Password (not normal password)
SMTP_HOST     = os.getenv("SMTP_HOST")
SMTP_PORT     = int(os.getenv("SMTP_PORT"))
# ─────────────────────────────────────────────────────────────
if not SMTP_EMAIL or not SMTP_PASSWORD:
    raise ValueError("SMTP_EMAIL and SMTP_PASSWORD environment variables must be set. Please set them to your Gmail address and an App Password respectively.")
def _send_email(to_email: str, subject: str, body: str):
    """INternal helper -send any HTML email"""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
def send_otp_email(to_email: str, otp: str):
    subject = "Your Password Reset OTP — Intern Portal"
    body = f"""
    <div style="font-family:sans-serif;max-width:400px;margin:auto;padding:2rem;border:1px solid #eee;border-radius:12px">
      <h2 style="color:#667eea">🔐 Password Reset</h2>
      <p>You requested a password reset for your Intern Portal account.</p>
      <div style="text-align:center;margin:2rem 0">
        <span style="font-size:2.5rem;font-weight:bold;letter-spacing:0.5rem;color:#333">
          {otp}
        </span>
      </div>
      <p style="color:#888;font-size:0.9rem">This OTP expires in <strong>10 minutes</strong>.</p>
      <p style="color:#888;font-size:0.9rem">If you didn't request this, ignore this email.</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SMTP_EMAIL
    msg["To"]      = to_email
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())

def send_welcome_email(to_email: str, name: str, password: str, role: str):
    """Sends welcome email with login credentials to new user"""
    role_color = "#6b46c1" if role == "admin" else "#276749"
    role_bg    = "#ede9fe"  if role == "admin" else "#c6f6d5"

    body = f"""
    <div style="font-family:sans-serif;max-width:520px;margin:auto;
                padding:2rem;border:1px solid #eee;border-radius:16px">

      <!-- Header -->
      <div style="text-align:center;margin-bottom:1.5rem">
        <h1 style="font-size:2.5rem;margin:0">👨‍💼</h1>
        <h2 style="color:#667eea;margin:0.5rem 0">Welcome to Intern Portal!</h2>
        <p style="color:#888;font-size:0.9rem;margin:0">
          Your account has been created by an admin.
        </p>
      </div>

      <!-- Welcome message -->
      <p style="color:#333">Hi <strong>{name}</strong>,</p>
      <p style="color:#555;line-height:1.6">
        Your account is ready. Use the credentials below to log in.
        We recommend changing your password after your first login.
      </p>

      <!-- Credentials Box -->
      <div style="background:#f8f9fa;border-radius:12px;
                  padding:1.5rem;margin:1.5rem 0;border:1px solid #eee">
        <h3 style="margin:0 0 1rem 0;color:#333;font-size:1rem">
          🔑 Your Login Credentials
        </h3>

        <table style="width:100%;border-collapse:collapse">
          <tr>
            <td style="padding:0.5rem 0;color:#888;font-size:0.9rem;width:100px">
              Email
            </td>
            <td style="padding:0.5rem 0;color:#333;font-weight:600;font-size:0.9rem">
              {to_email}
            </td>
          </tr>
          <tr>
            <td style="padding:0.5rem 0;color:#888;font-size:0.9rem">
              Password
            </td>
            <td style="padding:0.5rem 0;font-size:0.9rem">
              <span style="background:#fff;border:1px solid #ddd;
                           border-radius:6px;padding:0.3rem 0.8rem;
                           font-family:monospace;font-weight:600;
                           letter-spacing:0.05rem;color:#333">
                {password}
              </span>
            </td>
          </tr>
          <tr>
            <td style="padding:0.5rem 0;color:#888;font-size:0.9rem">
              Role
            </td>
            <td style="padding:0.5rem 0">
              <span style="background:{role_bg};color:{role_color};
                           padding:0.2rem 0.75rem;border-radius:20px;
                           font-size:0.8rem;font-weight:700;
                           text-transform:uppercase">
                {role}
              </span>
            </td>
          </tr>
        </table>
      </div>

      <!-- Warning -->
      <div style="background:#fffbeb;border:1px solid #fcd34d;
                  border-radius:8px;padding:0.9rem 1rem;margin-bottom:1.5rem">
        <p style="margin:0;color:#92400e;font-size:0.85rem">
          ⚠️ <strong>Important:</strong> Please change your password after
          your first login for security.
        </p>
      </div>

      <!-- Footer -->
      <p style="color:#aaa;font-size:0.8rem;text-align:center;margin:0">
        This email was sent by Intern Portal. Do not share your credentials.
      </p>
    </div>
    """
    _send_email(
        to_email,
        "🎉 Welcome to Intern Portal — Your Account Details",
        body
    )
    
