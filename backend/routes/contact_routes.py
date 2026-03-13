"""Contact form and support ticket routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

router = APIRouter(prefix="/api", tags=["Contact"])

db = None

def set_database(database):
    global db
    db = database

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    phone: str = ""
    message: str

class SupportTicket(BaseModel):
    subject: str
    message: str
    priority: str = "medium"

NOTIFICATION_EMAIL = "techmeliora@gmail.com"

@router.post("/contact")
async def submit_contact_form(form: ContactForm):
    """Submit contact form and store in DB"""
    contact_doc = {
        "name": form.name,
        "email": form.email,
        "company": form.company,
        "phone": form.phone,
        "message": form.message,
        "status": "new",
        "created_at": datetime.utcnow()
    }
    await db.contact_submissions.insert_one(contact_doc)
    
    # Try to send email notification
    try:
        _send_notification_email(form)
    except Exception as e:
        logging.warning(f"Email notification failed: {e}")
    
    return {"success": True, "message": "Your message has been received. We will contact you soon."}

def _send_notification_email(form: ContactForm):
    """Send email notification about new contact form submission"""
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    if not smtp_user or not smtp_pass:
        logging.info("SMTP not configured - skipping email notification")
        return
    
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = NOTIFICATION_EMAIL
    msg["Subject"] = f"New Contact Form: {form.name} - {form.company or 'N/A'}"
    
    body = f"""
New contact form submission on Analiyx:

Name: {form.name}
Email: {form.email}
Company: {form.company or 'N/A'}
Phone: {form.phone or 'N/A'}

Message:
{form.message}
    """
    msg.attach(MIMEText(body, "plain"))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
