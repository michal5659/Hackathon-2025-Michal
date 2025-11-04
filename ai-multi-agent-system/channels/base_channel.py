"""
Base Channel Handler
Abstract base class for all message channel handlers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseChannelHandler(ABC):
    """Abstract base class for channel handlers"""
    
    def __init__(self, channel_name: str):
        self.channel_name = channel_name
        self.logger = get_logger(f"{__name__}.{channel_name}")
    
    @abstractmethod
    async def pull_messages(self) -> List[Dict[str, Any]]:
        """
        Pull new messages from the channel
        
        Returns:
            List of message dictionaries with standardized format:
            {
                'message_id': str,
                'channel': str,
                'sender': str,
                'content': str,
                'timestamp': str,
                'metadata': dict
            }
        """
        pass
    
    @abstractmethod
    async def send_message(self, recipient: str, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Send a message through the channel
        
        Args:
            recipient: Recipient identifier
            content: Message content
            metadata: Additional metadata
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read/processed
        
        Args:
            message_id: Message identifier
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def standardize_message(self, raw_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert channel-specific message format to standardized format
        
        Args:
            raw_message: Channel-specific message data
        
        Returns:
            Standardized message dictionary
        """
        return {
            'message_id': raw_message.get('id', 'unknown'),
            'channel': self.channel_name,
            'sender': raw_message.get('from', 'unknown'),
            'content': raw_message.get('body', raw_message.get('text', '')),
            'timestamp': raw_message.get('timestamp', ''),
            'metadata': raw_message.get('metadata', {})
        }
