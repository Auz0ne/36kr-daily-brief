"""Email sender — self-sent via Gmail SMTP."""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import re


def markdown_to_html(text: str) -> str:
    """Basic markdown-to-HTML conversion for email rendering."""
    # Headers
    text = re.sub(r'^### (.+)$', r'<h3 style="color:#1a1a2e;margin-top:20px;">\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2 style="color:#1a1a2e;margin-top:24px;border-bottom:1px solid #eee;padding-bottom:6px;">\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1 style="color:#1a1a2e;">\1</h1>', text, flags=re.MULTILINE)
    
    # Bold and italic
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    
    # Bullet points
    text = re.sub(r'^- (.+)$', r'<li style="margin-bottom:4px;">\1</li>', text, flags=re.MULTILINE)
    # Wrap consecutive <li> in <ul>
    text = re.sub(r'((?:<li[^>]*>.*?</li>\n?)+)', r'<ul style="padding-left:20px;">\1</ul>', text)
    
    # Line breaks for remaining plain text
    text = re.sub(r'\n\n', '</p><p style="margin:12px 0;line-height:1.6;">', text)
    text = f'<p style="margin:12px 0;line-height:1.6;">{text}</p>'
    
    return text


def build_email_html(brief_content: str, date_str: str) -> str:
    """Wrap brief content in a clean HTML email template."""
    brief_html = markdown_to_html(brief_content)
    
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
             max-width: 680px; margin: 0 auto; padding: 20px; color: #333; background: #fafafa;">
  
  <div style="background: white; border-radius: 8px; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    
    <div style="text-align: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 2px solid #e74c3c;">
      <h1 style="margin: 0; font-size: 22px; color: #1a1a2e;">🇨🇳 36kr Daily Brief</h1>
      <p style="margin: 4px 0 0; color: #888; font-size: 14px;">{date_str}</p>
    </div>
    
    {brief_html}
    
    <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; 
                font-size: 12px; color: #999; text-align: center;">
      Auto-generated from 36kr.com via Claude API · 
      <a href="https://36kr.com" style="color:#999;">Source</a>
    </div>
    
  </div>
</body>
</html>"""


def send_brief_email(brief_content: str):
    """Send the brief as a self-sent HTML email via Gmail SMTP."""
    email = os.environ["SMTP_EMAIL"]
    password = os.environ["SMTP_PASSWORD"]
    
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    subject = f"🇨🇳 36kr Daily Brief — {datetime.now().strftime('%b %d, %Y')}"
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email
    msg["To"] = email  # Self-sent
    
    # Plain text fallback
    msg.attach(MIMEText(brief_content, "plain", "utf-8"))
    
    # HTML version
    html = build_email_html(brief_content, date_str)
    msg.attach(MIMEText(html, "html", "utf-8"))
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
    
    print(f"✅ Brief sent to {email}")


def send_error_email(error_msg: str):
    """Send a short error notification if the brief fails."""
    email = os.environ["SMTP_EMAIL"]
    password = os.environ["SMTP_PASSWORD"]
    
    msg = MIMEText(f"36kr Daily Brief failed today.\n\nError: {error_msg}\n\nWill retry tomorrow.", "plain", "utf-8")
    msg["Subject"] = f"⚠️ 36kr Brief — Error {datetime.now().strftime('%b %d')}"
    msg["From"] = email
    msg["To"] = email
    
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(email, password)
        server.send_message(msg)
    
    print(f"⚠️ Error notification sent to {email}")
