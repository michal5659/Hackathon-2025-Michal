"""
Email Channel Handler
Handles email message retrieval and sending via IMAP/SMTP
"""
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from datetime import datetime
from .base_channel import BaseChannelHandler
from config.settings import settings


class EmailChannelHandler(BaseChannelHandler):
    """Email channel handler using IMAP and SMTP"""
    
    def __init__(self):
        super().__init__("email")
        self.imap_server = settings.email.imap_server
        self.imap_port = settings.email.imap_port
        self.smtp_server = settings.email.smtp_server
        self.smtp_port = settings.email.smtp_port
        self.username = settings.email.username
        self.password = settings.email.password
        self.processed_messages = set()
    
    async def pull_messages(self) -> List[Dict[str, Any]]:
        """Pull new unread emails from inbox"""
        try:
            self.logger.info("Connecting to email server...")
            
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            mail.select('inbox')
            
            # Search for unread messages
            status, message_ids = mail.search(None, 'UNSEEN')
            
            if status != 'OK':
                self.logger.warning("No new messages found")
                return []
            
            messages = []
            message_id_list = message_ids[0].split()
            
            for msg_id in message_id_list:
                if msg_id in self.processed_messages:
                    continue
                
                # Fetch message
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                # Parse email
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract message content
                standardized_message = self._parse_email_message(email_message, msg_id.decode())
                messages.append(standardized_message)
                
                self.processed_messages.add(msg_id)
            
            mail.close()
            mail.logout()
            
            self.logger.info(f"Pulled {len(messages)} new email messages")
            return messages
            
        except Exception as e:
            self.logger.error(f"Error pulling email messages: {str(e)}")
            return []
    
    async def send_message(self, recipient: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send an email message"""
        try:
            self.logger.info(f"Sending email to {recipient}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = recipient
            msg['Subject'] = metadata.get('subject', 'Response to your inquiry') if metadata else 'Response to your inquiry'
            
            # Add body
            body = MIMEText(content, 'plain')
            msg.attach(body)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark email as read"""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.username, self.password)
            mail.select('inbox')
            
            # Mark as seen
            mail.store(message_id.encode(), '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking email as read: {str(e)}")
            return False
    
    def _parse_email_message(self, email_message, msg_id: str) -> Dict[str, Any]:
        """Parse email message into standardized format"""
        # Extract sender
        from_addr = email.utils.parseaddr(email_message.get('From', ''))[1]
        
        # Extract subject
        subject = email_message.get('Subject', 'No Subject')
        
        # Extract body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        body = str(part.get_payload())
                    break
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                body = str(email_message.get_payload())
        
        # Extract timestamp
        date_str = email_message.get('Date', '')
        try:
            timestamp = email.utils.parsedate_to_datetime(date_str).isoformat()
        except:
            timestamp = datetime.utcnow().isoformat()
        
        return {
            'message_id': msg_id,
            'channel': 'email',
            'sender': from_addr,
            'content': body.strip(),
            'timestamp': timestamp,
            'metadata': {
                'subject': subject,
                'to': email_message.get('To', ''),
                'cc': email_message.get('Cc', ''),
            }
        }


# Singleton instance
_email_handler = None

def get_email_handler() -> EmailChannelHandler:
    """Get or create email handler singleton"""
    global _email_handler
    if _email_handler is None:
        _email_handler = EmailChannelHandler()
    return _email_handler
