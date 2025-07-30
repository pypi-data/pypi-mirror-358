"""
Email utilities for sending notifications using SMTP or Azure Communication Services
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Try to import Azure Communication Services
try:
    from azure.communication.email import EmailClient
    AZURE_EMAIL_AVAILABLE = True
except ImportError:
    AZURE_EMAIL_AVAILABLE = False

from config import settings

logger = logging.getLogger(__name__)

def send_email_smtp(recipient_email, subject, body, html_content=None, attachments=None):
    """
    Send an email using SMTP protocol
    
    Args:
        recipient_email: The recipient's email address
        subject: Email subject
        body: Plain text email body
        html_content: Optional HTML content
        attachments: List of file paths to attach
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create a multipart message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_SENDER
        msg['To'] = recipient_email
        
        # Add plain text content
        msg.attach(MIMEText(body, 'plain'))
        
        # Add HTML content if provided
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                with open(file_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=os.path.basename(file_path))
                    part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                    msg.attach(part)
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Email sent to {recipient_email} with subject '{subject}'")
        return True
    except Exception as e:
        logger.error(f"Error sending email via SMTP: {str(e)}")
        return False

def send_email_azure(recipient_email, subject, body, html_content=None):
    """
    Send an email using Azure Communication Services
    
    Args:
        recipient_email: The recipient's email address
        subject: Email subject
        body: Plain text email body
        html_content: Optional HTML content
        
    Returns:
        True if sent successfully, False otherwise
    """
    if not AZURE_EMAIL_AVAILABLE:
        logger.error("Azure Communication Services not available. Install with 'pip install azure-communication-email'")
        return False
    
    try:
        # Create the email client
        email_client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION_STRING)
        
        # Use HTML content if provided, otherwise use plain text
        content = html_content if html_content else body
        content_type = "html" if html_content else "plainText"
        
        # Create the email message
        message = {
            "senderAddress": settings.AZURE_COMMUNICATION_SENDER_EMAIL,
            "recipients": {
                "to": [{"address": recipient_email}]
            },
            "content": {
                "subject": subject,
                "plainText": body,
                "html": content if content_type == "html" else None
            }
        }
        
        # Send the email
        poller = email_client.begin_send(message)
        result = poller.result()
        
        logger.info(f"Email sent to {recipient_email} with subject '{subject}' via Azure Communication Services")
        return True
    except Exception as e:
        logger.error(f"Error sending email via Azure Communication Services: {str(e)}")
        return False

def send_email(recipient_email, subject, body, html_content=None, attachments=None, use_azure=False):
    """
    Send an email using the preferred method (SMTP or Azure Communication Services)
    
    Args:
        recipient_email: The recipient's email address
        subject: Email subject
        body: Plain text email body
        html_content: Optional HTML content
        attachments: List of file paths to attach (only used with SMTP)
        use_azure: Force using Azure Communication Services if available
        
    Returns:
        True if sent successfully, False otherwise
    """
    # Use Azure if requested and available
    if use_azure and AZURE_EMAIL_AVAILABLE and settings.AZURE_COMMUNICATION_CONNECTION_STRING:
        return send_email_azure(recipient_email, subject, body, html_content)
    
    # Fall back to SMTP
    return send_email_smtp(recipient_email, subject, body, html_content, attachments)
