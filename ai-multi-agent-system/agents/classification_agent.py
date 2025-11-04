"""
Classification Agent
Classifies incoming messages using Azure OpenAI LLM
"""
from crewai import Agent, Task
from langchain_openai import AzureChatOpenAI
from typing import Dict, Any
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class ClassificationAgent:
    """
    Agent responsible for classifying incoming messages
    Returns structured JSON with Action ID and IVO attributes
    """
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM"""
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai.endpoint,
            api_key=settings.azure_openai.api_key,
            api_version=settings.azure_openai.api_version,
            deployment_name=settings.azure_openai.deployment_name,
            model=settings.azure_openai.model,
            temperature=0.3
        )
    
    def _create_agent(self) -> Agent:
        """Create the classification agent"""
        return Agent(
            role="Message Classification Specialist",
            goal="Accurately classify incoming messages and extract relevant attributes for task creation",
            backstory="""You are an expert in analyzing customer messages and categorizing them 
            into actionable categories. You understand context, intent, and urgency. You extract 
            key information needed for task execution including customer details, issue type, 
            priority, and required actions.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def classify_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a message and return structured classification result
        
        Args:
            message: Dict containing message content and metadata
                - content: The message text
                - channel: Source channel (email, whatsapp, teams)
                - sender: Sender information
                - timestamp: Message timestamp
        
        Returns:
            Dict containing:
                - action_id: Classified action identifier
                - ivo_attributes: Dictionary of IDIT IVO attributes
                - confidence: Classification confidence score
                - category: Message category
        """
        try:
            logger.info(f"Classifying message from {message.get('channel', 'unknown')}")
            
            # Create classification task
            task = Task(
                description=self._build_classification_prompt(message),
                agent=self.agent,
                expected_output="""JSON object with the following structure:
                {
                    "action_id": "string (e.g., 'policy_inquiry', 'claim_submission', 'update_details')",
                    "category": "string (e.g., 'inquiry', 'claim', 'complaint', 'update')",
                    "ivo_attributes": {
                        "customer_id": "string",
                        "policy_number": "string or null",
                        "issue_type": "string",
                        "priority": "string (low, medium, high, urgent)",
                        "required_action": "string",
                        "extracted_entities": {}
                    },
                    "confidence": float (0.0 to 1.0)
                }"""
            )
            
            # Execute classification
            result = task.execute()
            
            logger.info(f"Message classified successfully with action_id: {result.get('action_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error classifying message: {str(e)}")
            return self._get_fallback_classification(message)
    
    def _build_classification_prompt(self, message: Dict[str, Any]) -> str:
        """Build the classification prompt for the LLM"""
        return f"""
        Analyze the following message and classify it into an appropriate action category.
        Extract all relevant attributes for task processing.
        
        Message Details:
        - Channel: {message.get('channel', 'unknown')}
        - Sender: {message.get('sender', 'unknown')}
        - Timestamp: {message.get('timestamp', 'unknown')}
        - Content: {message.get('content', '')}
        
        Classification Guidelines:
        1. Identify the primary intent and action required
        2. Extract customer identifiers (ID, policy number, etc.)
        3. Determine the issue type and category
        4. Assess priority based on urgency indicators
        5. Extract any mentioned entities (dates, amounts, names, etc.)
        
        Common Action IDs:
        - policy_inquiry: Questions about existing policies
        - claim_submission: New claim requests
        - claim_status: Checking claim status
        - policy_update: Updating policy details
        - payment_inquiry: Payment-related questions
        - complaint: Customer complaints
        - general_inquiry: General questions
        - document_request: Requesting documents
        
        Return a structured JSON classification with all extracted information.
        """
    
    def _get_fallback_classification(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback classification if LLM fails"""
        return {
            "action_id": "general_inquiry",
            "category": "inquiry",
            "ivo_attributes": {
                "customer_id": message.get('sender', 'unknown'),
                "policy_number": None,
                "issue_type": "unclassified",
                "priority": "medium",
                "required_action": "manual_review",
                "extracted_entities": {}
            },
            "confidence": 0.5
        }


# Singleton instance
_classification_agent = None

def get_classification_agent() -> ClassificationAgent:
    """Get or create classification agent singleton"""
    global _classification_agent
    if _classification_agent is None:
        _classification_agent = ClassificationAgent()
    return _classification_agent
