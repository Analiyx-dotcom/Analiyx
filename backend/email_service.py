"""Email notification service using Gmail SMTP"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

def send_email(to_email: str, subject: str, html_body: str):
    """Send an email via Gmail SMTP"""
    smtp_email = os.environ.get("SMTP_EMAIL")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))

    if not smtp_email or not smtp_password:
        logging.warning("SMTP not configured, skipping email")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Analiyx <{smtp_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, to_email, msg.as_string())

        logging.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email to {to_email}: {str(e)}")
        return False

def send_ticket_notification(user_email: str, user_name: str, subject: str, message: str):
    """Notify admin when a new support ticket is created"""
    admin_email = os.environ.get("SMTP_EMAIL", "analiyx26@gmail.com")
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#1a1a2e;color:#fff;padding:30px;border-radius:12px;">
        <h2 style="color:#a855f7;">New Support Ticket</h2>
        <p><strong>From:</strong> {user_name} ({user_email})</p>
        <p><strong>Subject:</strong> {subject}</p>
        <div style="background:#16213e;padding:15px;border-radius:8px;margin:15px 0;">
            <p style="color:#e2e8f0;">{message}</p>
        </div>
        <p style="color:#94a3b8;font-size:12px;">Login to Analiyx Admin to reply.</p>
    </div>
    """
    return send_email(admin_email, f"[Ticket] {subject} - from {user_name}", html)

def send_ticket_reply_notification(user_email: str, user_name: str, subject: str, reply: str):
    """Notify user when admin replies to their ticket"""
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#1a1a2e;color:#fff;padding:30px;border-radius:12px;">
        <h2 style="color:#a855f7;">Analiyx Support Reply</h2>
        <p>Hi {user_name},</p>
        <p>Your ticket <strong>"{subject}"</strong> has received a reply:</p>
        <div style="background:#16213e;padding:15px;border-radius:8px;margin:15px 0;border-left:3px solid #a855f7;">
            <p style="color:#e2e8f0;">{reply}</p>
        </div>
        <p style="color:#94a3b8;font-size:12px;">Login to your Analiyx dashboard to view the full conversation.</p>
    </div>
    """
    return send_email(user_email, f"Re: {subject} - Analiyx Support", html)

def send_welcome_email(user_email: str, user_name: str):
    """Send welcome email to new users"""
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#1a1a2e;color:#fff;padding:30px;border-radius:12px;">
        <h2 style="color:#a855f7;">Welcome to Analiyx!</h2>
        <p>Hi {user_name},</p>
        <p>Your 7-day free trial has started. Here's what you can do:</p>
        <ul style="color:#e2e8f0;">
            <li>Connect Google Ads, Analytics & Meta Ads</li>
            <li>Upload Excel/CSV data for AI analysis</li>
            <li>Ask AI anything about your data</li>
            <li>Get AI Visibility scores for your URLs</li>
        </ul>
        <p>After your trial, choose a plan starting at ₹6,000/year.</p>
        <p style="color:#94a3b8;font-size:12px;">- Team Analiyx</p>
    </div>
    """
    return send_email(user_email, "Welcome to Analiyx - Your 7-Day Trial Has Started!", html)

def send_payment_confirmation(user_email: str, user_name: str, plan: str, amount: int, expiry_date: str):
    """Send payment confirmation email"""
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#1a1a2e;color:#fff;padding:30px;border-radius:12px;">
        <h2 style="color:#a855f7;">Payment Confirmed!</h2>
        <p>Hi {user_name},</p>
        <p>Your payment has been processed successfully.</p>
        <div style="background:#16213e;padding:15px;border-radius:8px;margin:15px 0;">
            <p><strong>Plan:</strong> {plan}</p>
            <p><strong>Amount:</strong> ₹{amount:,}</p>
            <p><strong>Valid Until:</strong> {expiry_date}</p>
        </div>
        <p>All features are now active on your account.</p>
        <p style="color:#94a3b8;font-size:12px;">- Team Analiyx</p>
    </div>
    """
    return send_email(user_email, f"Analiyx - Payment Confirmed ({plan} Plan)", html)
