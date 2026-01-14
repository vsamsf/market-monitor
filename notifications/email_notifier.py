"""Email notification implementation."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from notifications.notifier import Notifier
from utils.logger import get_logger

logger = get_logger(__name__)


class EmailNotifier(Notifier):
    """Email notification using SMTP."""
    
    def __init__(
        self,
        enabled: bool = False,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 587,
        use_tls: bool = True,
        sender_email: str = "",
        sender_password: str = "",
        recipient_email: str = ""
    ):
        """
        Initialize email notifier.
        
        Args:
            enabled: Whether email notifications are enabled
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            use_tls: Whether to use TLS
            sender_email: Sender email address
            sender_password: Sender email password/app password
            recipient_email: Recipient email address
        """
        super().__init__(enabled)
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.use_tls = use_tls
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        
        # Validate configuration
        if enabled and not all([sender_email, sender_password, recipient_email]):
            logger.warning("Email notifier enabled but missing credentials")
            self.enabled = False
    
    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send email notification.
        
        Args:
            title: Email subject
            message: Email body
            priority: Priority level (affects subject prefix)
        
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Add priority prefix to subject
            priority_prefix = {
                'low': '',
                'normal': '',
                'high': '[IMPORTANT] ',
                'critical': '[URGENT] '
            }.get(priority, '')
            
            msg['Subject'] = f"{priority_prefix}{title}"
            
            # Create HTML version
            html_message = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2 style="color: #2c3e50;">{title}</h2>
                    <div style="white-space: pre-wrap; line-height: 1.6;">
                        {message}
                    </div>
                    <hr>
                    <p style="color: #7f8c8d; font-size: 0.9em;">
                        This is an automated notification from Market Monitor & Productivity System.
                    </p>
                </body>
            </html>
            """
            
            # Attach both plain text and HTML
            msg.attach(MIMEText(message, 'plain'))
            msg.attach(MIMEText(html_message, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {self.recipient_email}: {title}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check email and password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
