"""
Teams Channel Handler
Handles Microsoft Teams message retrieval and sending
"""
import httpx
import pymsteams
from typing import Dict, Any, List
from datetime import datetime
from .base_channel import BaseChannelHandler
from config.settings import settings


class TeamsChannelHandler(BaseChannelHandler):
    """Microsoft Teams channel handler"""
    
    def __init__(self):
        super().__init__("teams")
        self.webhook_url = settings.teams.webhook_url
        self.bot_id = settings.teams.bot_id
        self.bot_password = settings.teams.bot_password
        self.app_id = settings.teams.app_id
        self.processed_messages = set()
    
    async def pull_messages(self) -> List[Dict[str, Any]]:
        """
        Pull new Teams messages
        Note: Teams typically uses Bot Framework for message handling
        This is a simplified implementation
        """
        try:
            self.logger.info("Fetching Teams messages...")
            
            # Teams messages are typically received via Bot Framework webhooks
            # This method would be called by a bot activity handler
            # For now, we return empty list and rely on webhook processing
            
            self.logger.info("Teams message pulling requires Bot Framework webhook integration")
            return []
            
        except Exception as e:
            self.logger.error(f"Error pulling Teams messages: {str(e)}")
            return []
    
    async def send_message(self, recipient: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """Send a message to Teams channel via webhook"""
        try:
            self.logger.info(f"Sending Teams message to {recipient}")
            
            # Create Teams message card
            teams_message = pymsteams.connectorcard(self.webhook_url)
            
            # Set message title and text
            if metadata and metadata.get('title'):
                teams_message.title(metadata['title'])
            
            teams_message.text(content)
            
            # Add color based on message type
            if metadata:
                if metadata.get('type') == 'error':
                    teams_message.color('FF0000')  # Red
                elif metadata.get('type') == 'success':
                    teams_message.color('00FF00')  # Green
                elif metadata.get('type') == 'warning':
                    teams_message.color('FFA500')  # Orange
                else:
                    teams_message.color('0078D4')  # Blue (default Teams color)
            
            # Add sections if provided
            if metadata and metadata.get('sections'):
                for section_data in metadata['sections']:
                    section = pymsteams.cardsection()
                    section.title(section_data.get('title', ''))
                    section.text(section_data.get('text', ''))
                    teams_message.addSection(section)
            
            # Send message
            teams_message.send()
            
            self.logger.info(f"Teams message sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Teams message: {str(e)}")
            return False
    
    async def send_adaptive_card(self, recipient: str, card_data: Dict[str, Any]) -> bool:
        """Send an Adaptive Card to Teams"""
        try:
            self.logger.info(f"Sending Teams Adaptive Card to {recipient}")
            
            teams_message = pymsteams.connectorcard(self.webhook_url)
            
            # Set payload for Adaptive Card
            teams_message.payload = card_data
            
            # Send card
            teams_message.send()
            
            self.logger.info("Teams Adaptive Card sent successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Teams Adaptive Card: {str(e)}")
            return False
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark Teams message as read"""
        try:
            # Teams Bot Framework handles read receipts differently
            # This would require Bot Framework SDK integration
            self.logger.info(f"Marking Teams message {message_id} as read")
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking Teams message as read: {str(e)}")
            return False
    
    def _parse_teams_message(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Teams Bot Framework activity into standardized format"""
        # Extract message content
        content = activity.get('text', '')
        
        # Extract sender information
        sender_info = activity.get('from', {})
        sender = sender_info.get('name', sender_info.get('id', 'unknown'))
        
        # Extract timestamp
        timestamp = activity.get('timestamp', datetime.utcnow().isoformat())
        
        # Extract conversation info
        conversation = activity.get('conversation', {})
        
        return {
            'message_id': activity.get('id', 'unknown'),
            'channel': 'teams',
            'sender': sender,
            'content': content,
            'timestamp': timestamp,
            'metadata': {
                'conversation_id': conversation.get('id', ''),
                'channel_id': activity.get('channelId', ''),
                'service_url': activity.get('serviceUrl', ''),
                'recipient': activity.get('recipient', {}).get('name', ''),
                'activity_type': activity.get('type', 'message')
            }
        }
    
    async def handle_webhook(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming Teams Bot Framework activity
        
        Args:
            activity: Bot Framework activity object
        
        Returns:
            Standardized message
        """
        try:
            message_id = activity.get('id')
            
            if message_id and message_id not in self.processed_messages:
                standardized_message = self._parse_teams_message(activity)
                self.processed_messages.add(message_id)
                return standardized_message
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error handling Teams webhook: {str(e)}")
            return None
    
    async def send_typing_indicator(self, conversation_id: str) -> bool:
        """Send typing indicator to Teams conversation"""
        try:
            # This would require Bot Framework SDK
            # Placeholder implementation
            self.logger.info(f"Sending typing indicator to conversation {conversation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending typing indicator: {str(e)}")
            return False
    
    def create_adaptive_card_response(
        self, 
        title: str, 
        message: str, 
        facts: List[Dict[str, str]] = None,
        actions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an Adaptive Card payload for rich Teams messages
        
        Args:
            title: Card title
            message: Main message text
            facts: List of fact dictionaries with 'name' and 'value' keys
            actions: List of action button definitions
        
        Returns:
            Adaptive Card JSON payload
        """
        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": title,
                                "weight": "bolder",
                                "size": "large",
                                "wrap": True
                            },
                            {
                                "type": "TextBlock",
                                "text": message,
                                "wrap": True,
                                "spacing": "medium"
                            }
                        ]
                    }
                }
            ]
        }
        
        # Add facts if provided
        if facts:
            fact_set = {
                "type": "FactSet",
                "facts": [{"title": f['name'], "value": f['value']} for f in facts]
            }
            card["attachments"][0]["content"]["body"].append(fact_set)
        
        # Add actions if provided
        if actions:
            card["attachments"][0]["content"]["actions"] = actions
        
        return card


# Singleton instance
_teams_handler = None

def get_teams_handler() -> TeamsChannelHandler:
    """Get or create Teams handler singleton"""
    global _teams_handler
    if _teams_handler is None:
        _teams_handler = TeamsChannelHandler()
    return _teams_handler
