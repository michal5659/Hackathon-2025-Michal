"""
WhatsApp Channel Handler
Handles WhatsApp message retrieval and sending via WhatsApp Business API
"""
import httpx
from typing import Dict, Any, List
from datetime import datetime
from .base_channel import BaseChannelHandler
from config.settings import settings


class WhatsAppChannelHandler(BaseChannelHandler):
    """WhatsApp channel handler using WhatsApp Business API"""
    
    def __init__(self):
        super().__init__("whatsapp")
        self.api_url = settings.whatsapp.api_url
        self.access_token = settings.whatsapp.access_token
        self.phone_number_id = settings.whatsapp.phone_number_id
        self.business_account_id = settings.whatsapp.business_account_id
        self.processed_messages = set()
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    async def pull_messages(self) -> List[Dict[str, Any]]:
        """Pull new WhatsApp messages"""
        try:
            self.logger.info("Fetching WhatsApp messages...")
            
            # WhatsApp uses webhook for incoming messages
            # This method would typically be called by a webhook handler
            # For polling, we'd use the Messages API endpoint
            
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{self.phone_number_id}/messages"
                
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    self.logger.error(f"WhatsApp API error: {response.status_code}")
                    return []
                
                data = response.json()
                messages = []
                
                # Parse messages
                for msg_data in data.get('messages', []):
                    msg_id = msg_data.get('id')
                    
                    if msg_id in self.processed_messages:
                        continue
                    
                    standardized_message = self._parse_whatsapp_message(msg_data)
                    messages.append(standardized_message)
                    
                    self.processed_messages.add(msg_id)
                
                self.logger.info(f"Pulled {len(messages)} new WhatsApp messages")
                return messages
                
        except Exception as e:
            self.logger.error(f"Error pulling WhatsApp messages: {str(e)}")
            return []
    
    async def send_message(self, recipient: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send a WhatsApp message"""
        try:
            self.logger.info(f"Sending WhatsApp message to {recipient}")
            
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{self.phone_number_id}/messages"
                
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": recipient,
                    "type": "text",
                    "text": {
                        "preview_url": False,
                        "body": content
                    }
                }
                
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    self.logger.info(f"WhatsApp message sent successfully to {recipient}")
                    return True
                else:
                    self.logger.error(f"WhatsApp send failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark WhatsApp message as read"""
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_url}/{self.phone_number_id}/messages"
                
                payload = {
                    "messaging_product": "whatsapp",
                    "status": "read",
                    "message_id": message_id
                }
                
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                
                return response.status_code == 200
                
        except Exception as e:
            self.logger.error(f"Error marking WhatsApp message as read: {str(e)}")
            return False
    
    def _parse_whatsapp_message(self, msg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse WhatsApp message into standardized format"""
        # Extract message content based on type
        content = ""
        msg_type = msg_data.get('type', 'text')
        
        if msg_type == 'text':
            content = msg_data.get('text', {}).get('body', '')
        elif msg_type == 'image':
            content = f"[Image] {msg_data.get('image', {}).get('caption', '')}"
        elif msg_type == 'document':
            content = f"[Document] {msg_data.get('document', {}).get('filename', '')}"
        elif msg_type == 'audio':
            content = "[Audio Message]"
        elif msg_type == 'video':
            content = f"[Video] {msg_data.get('video', {}).get('caption', '')}"
        
        # Extract timestamp
        timestamp_unix = msg_data.get('timestamp', 0)
        try:
            timestamp = datetime.fromtimestamp(int(timestamp_unix)).isoformat()
        except:
            timestamp = datetime.utcnow().isoformat()
        
        return {
            'message_id': msg_data.get('id', 'unknown'),
            'channel': 'whatsapp',
            'sender': msg_data.get('from', 'unknown'),
            'content': content,
            'timestamp': timestamp,
            'metadata': {
                'type': msg_type,
                'name': msg_data.get('profile', {}).get('name', ''),
                'context': msg_data.get('context', {})
            }
        }
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Handle incoming WhatsApp webhook data
        
        Args:
            webhook_data: Webhook payload from WhatsApp
        
        Returns:
            List of standardized messages
        """
        try:
            messages = []
            
            for entry in webhook_data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    for message in value.get('messages', []):
                        if message.get('id') not in self.processed_messages:
                            standardized_message = self._parse_whatsapp_message(message)
                            messages.append(standardized_message)
                            self.processed_messages.add(message.get('id'))
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error handling WhatsApp webhook: {str(e)}")
            return []


# Singleton instance
_whatsapp_handler = None

def get_whatsapp_handler() -> WhatsAppChannelHandler:
    """Get or create WhatsApp handler singleton"""
    global _whatsapp_handler
    if _whatsapp_handler is None:
        _whatsapp_handler = WhatsAppChannelHandler()
    return _whatsapp_handler
