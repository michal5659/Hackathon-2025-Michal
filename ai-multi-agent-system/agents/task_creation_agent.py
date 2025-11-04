"""
Task Creation Agent
Converts classification results into actionable tasks and IVO JSON format
"""
from crewai import Agent, Task
from langchain_openai import AzureChatOpenAI
from typing import Dict, Any
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class TaskCreationAgent:
    """
    Agent responsible for creating actionable tasks from classification results
    Generates IVO JSON Action for IDIT API integration
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
            temperature=0.2
        )
    
    def _create_agent(self) -> Agent:
        """Create the task creation agent"""
        return Agent(
            role="Task Creation Specialist",
            goal="Transform classification results into structured, executable tasks with proper IVO JSON formatting",
            backstory="""You are an expert in workflow automation and task management. 
            You excel at translating intent and requirements into precise, actionable tasks. 
            You understand the IDIT API structure and can format requests properly for seamless integration.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_task(self, classification: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an executable task from classification results
        
        Args:
            classification: Classification result from ClassificationAgent
            message: Original message data
        
        Returns:
            Dict containing:
                - task_id: Unique task identifier
                - action_type: Type of action to execute
                - ivo_json: Formatted IVO JSON for IDIT API
                - execution_params: Parameters for task execution
                - metadata: Additional task metadata
        """
        try:
            logger.info(f"Creating task for action_id: {classification.get('action_id')}")
            
            # Create task generation task
            task = Task(
                description=self._build_task_creation_prompt(classification, message),
                agent=self.agent,
                expected_output="""JSON object with the following structure:
                {
                    "task_id": "string (UUID format)",
                    "action_type": "string (matches action_id from classification)",
                    "ivo_json": {
                        "action_id": "string",
                        "request_type": "string",
                        "customer_data": {
                            "customer_id": "string",
                            "policy_number": "string or null",
                            "contact_info": {}
                        },
                        "action_parameters": {
                            "issue_type": "string",
                            "priority": "string",
                            "details": {},
                            "attachments": []
                        },
                        "metadata": {
                            "source_channel": "string",
                            "timestamp": "string",
                            "original_message_id": "string"
                        }
                    },
                    "execution_params": {
                        "api_endpoint": "string",
                        "http_method": "string",
                        "timeout": integer,
                        "retry_strategy": {}
                    },
                    "metadata": {
                        "created_at": "string",
                        "classification_confidence": float,
                        "estimated_completion_time": "string"
                    }
                }"""
            )
            
            # Execute task creation
            result = task.execute()
            
            logger.info(f"Task created successfully with task_id: {result.get('task_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return self._get_fallback_task(classification, message)
    
    def _build_task_creation_prompt(self, classification: Dict[str, Any], message: Dict[str, Any]) -> str:
        """Build the task creation prompt for the LLM"""
        return f"""
        Create a structured, executable task based on the following classification results and message data.
        
        Classification Results:
        - Action ID: {classification.get('action_id')}
        - Category: {classification.get('category')}
        - IVO Attributes: {classification.get('ivo_attributes')}
        - Confidence: {classification.get('confidence')}
        
        Original Message:
        - Channel: {message.get('channel')}
        - Sender: {message.get('sender')}
        - Content: {message.get('content')}
        - Message ID: {message.get('message_id')}
        
        Task Creation Guidelines:
        1. Generate a unique task_id (UUID format)
        2. Map action_id to appropriate IDIT API endpoint
        3. Structure IVO JSON according to IDIT API specification
        4. Include all relevant customer data and parameters
        5. Set appropriate execution parameters (endpoint, method, timeout)
        6. Add comprehensive metadata for tracking and auditing
        
        API Endpoint Mapping:
        - policy_inquiry -> /api/v1/policies/inquiry
        - claim_submission -> /api/v1/claims/submit
        - claim_status -> /api/v1/claims/status
        - policy_update -> /api/v1/policies/update
        - payment_inquiry -> /api/v1/payments/inquiry
        
        Ensure the IVO JSON is properly formatted and contains all necessary fields
        for successful API execution.
        """
    
    def _get_fallback_task(self, classification: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback task if LLM fails"""
        import uuid
        from datetime import datetime
        
        return {
            "task_id": str(uuid.uuid4()),
            "action_type": classification.get('action_id', 'general_inquiry'),
            "ivo_json": {
                "action_id": classification.get('action_id', 'general_inquiry'),
                "request_type": "manual_review",
                "customer_data": {
                    "customer_id": message.get('sender', 'unknown'),
                    "policy_number": None,
                    "contact_info": {}
                },
                "action_parameters": classification.get('ivo_attributes', {}),
                "metadata": {
                    "source_channel": message.get('channel', 'unknown'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "original_message_id": message.get('message_id', 'unknown')
                }
            },
            "execution_params": {
                "api_endpoint": "/api/v1/tasks/manual",
                "http_method": "POST",
                "timeout": 30,
                "retry_strategy": {"max_attempts": 3, "backoff": "exponential"}
            },
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "classification_confidence": classification.get('confidence', 0.5),
                "estimated_completion_time": "manual"
            }
        }


# Singleton instance
_task_creation_agent = None

def get_task_creation_agent() -> TaskCreationAgent:
    """Get or create task creation agent singleton"""
    global _task_creation_agent
    if _task_creation_agent is None:
        _task_creation_agent = TaskCreationAgent()
    return _task_creation_agent
