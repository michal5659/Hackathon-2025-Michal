"""
Message Pull Service
Coordinates message retrieval from all channels
"""
import asyncio
from typing import List, Dict, Any
from channels import get_email_handler, get_whatsapp_handler, get_teams_handler
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class MessagePullService:
    """Service for pulling messages from all channels"""
    
    def __init__(self):
        self.email_handler = get_email_handler()
        self.whatsapp_handler = get_whatsapp_handler()
        self.teams_handler = get_teams_handler()
        self.poll_interval = settings.app.message_poll_interval
        self.is_running = False
    
    async def pull_all_messages(self) -> List[Dict[str, Any]]:
        """
        Pull messages from all channels in parallel
        
        Returns:
            List of all messages from all channels
        """
        try:
            logger.info("Pulling messages from all channels...")
            
            # Pull messages from all channels concurrently
            results = await asyncio.gather(
                self.email_handler.pull_messages(),
                self.whatsapp_handler.pull_messages(),
                self.teams_handler.pull_messages(),
                return_exceptions=True
            )
            
            # Combine all messages
            all_messages = []
            for idx, result in enumerate(results):
                if isinstance(result, Exception):
                    channel_name = ['email', 'whatsapp', 'teams'][idx]
                    logger.error(f"Error pulling from {channel_name}: {str(result)}")
                else:
                    all_messages.extend(result)
            
            logger.info(f"Pulled {len(all_messages)} total messages from all channels")
            return all_messages
            
        except Exception as e:
            logger.error(f"Error in pull_all_messages: {str(e)}")
            return []
    
    async def pull_from_channel(self, channel_name: str) -> List[Dict[str, Any]]:
        """
        Pull messages from a specific channel
        
        Args:
            channel_name: Name of channel ('email', 'whatsapp', 'teams')
        
        Returns:
            List of messages from the specified channel
        """
        try:
            logger.info(f"Pulling messages from {channel_name}...")
            
            if channel_name.lower() == 'email':
                return await self.email_handler.pull_messages()
            elif channel_name.lower() == 'whatsapp':
                return await self.whatsapp_handler.pull_messages()
            elif channel_name.lower() == 'teams':
                return await self.teams_handler.pull_messages()
            else:
                logger.warning(f"Unknown channel: {channel_name}")
                return []
                
        except Exception as e:
            logger.error(f"Error pulling from {channel_name}: {str(e)}")
            return []
    
    async def start_polling(self, callback):
        """
        Start continuous polling of all channels
        
        Args:
            callback: Async function to call with new messages
        """
        self.is_running = True
        logger.info(f"Starting message polling (interval: {self.poll_interval}s)")
        
        while self.is_running:
            try:
                # Pull messages
                messages = await self.pull_all_messages()
                
                # Process messages if any found
                if messages:
                    logger.info(f"Processing {len(messages)} new messages")
                    await callback(messages)
                
                # Wait before next poll
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in polling loop: {str(e)}")
                await asyncio.sleep(self.poll_interval)
    
    def stop_polling(self):
        """Stop the polling loop"""
        logger.info("Stopping message polling")
        self.is_running = False
    
    async def send_response(self, channel: str, recipient: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Send a response message to the appropriate channel
        
        Args:
            channel: Channel name ('email', 'whatsapp', 'teams')
            recipient: Recipient identifier
            content: Message content
            metadata: Additional metadata
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            logger.info(f"Sending response via {channel} to {recipient}")
            
            if channel.lower() == 'email':
                return await self.email_handler.send_message(recipient, content, metadata)
            elif channel.lower() == 'whatsapp':
                return await self.whatsapp_handler.send_message(recipient, content, metadata)
            elif channel.lower() == 'teams':
                return await self.teams_handler.send_message(recipient, content, metadata)
            else:
                logger.warning(f"Unknown channel for sending: {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending response via {channel}: {str(e)}")
            return False


# Singleton instance
_message_pull_service = None

def get_message_pull_service() -> MessagePullService:
    """Get or create message pull service singleton"""
    global _message_pull_service
    if _message_pull_service is None:
        _message_pull_service = MessagePullService()
    return _message_pull_service
