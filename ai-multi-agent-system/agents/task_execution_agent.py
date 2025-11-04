"""
Task Execution Agent
Executes tasks by calling IDIT API and manages response handling
"""
from crewai import Agent, Task
from langchain_openai import AzureChatOpenAI
from typing import Dict, Any, Optional
from config.settings import settings
from utils.logger import get_logger
from services.idit_api_client import get_idit_client

logger = get_logger(__name__)


class TaskExecutionAgent:
    """
    Agent responsible for executing tasks via IDIT API
    Handles API calls, response processing, and reply generation
    """
    
    def __init__(self):
        self.llm = self._initialize_llm()
        self.agent = self._create_agent()
        self.idit_client = get_idit_client()
    
    def _initialize_llm(self) -> AzureChatOpenAI:
        """Initialize Azure OpenAI LLM"""
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai.endpoint,
            api_key=settings.azure_openai.api_key,
            api_version=settings.azure_openai.api_version,
            deployment_name=settings.azure_openai.deployment_name,
            model=settings.azure_openai.model,
            temperature=0.4
        )
    
    def _create_agent(self) -> Agent:
        """Create the task execution agent"""
        return Agent(
            role="Task Execution Specialist",
            goal="Execute tasks efficiently via IDIT API and generate appropriate user responses",
            backstory="""You are an expert in API integration and task execution. 
            You handle API calls reliably, manage errors gracefully, and craft clear, 
            helpful responses for users. You understand how to communicate technical 
            results in user-friendly language.""",
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    async def execute_task(self, task_data: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task via IDIT API and generate response
        
        Args:
            task_data: Task data from TaskCreationAgent
            message: Original message for context
        
        Returns:
            Dict containing:
                - execution_status: Status of execution (success, failed, pending)
                - api_response: Response from IDIT API
                - user_response: Formatted response message for user
                - metadata: Execution metadata
        """
        try:
            logger.info(f"Executing task: {task_data.get('task_id')}")
            
            # Execute API call
            api_response = await self._call_idit_api(task_data)
            
            # Generate user response based on API result
            user_response = await self._generate_user_response(
                task_data, 
                api_response, 
                message
            )
            
            result = {
                "execution_status": "success" if api_response.get('success') else "failed",
                "api_response": api_response,
                "user_response": user_response,
                "metadata": {
                    "task_id": task_data.get('task_id'),
                    "action_type": task_data.get('action_type'),
                    "channel": message.get('channel'),
                    "execution_time": api_response.get('execution_time')
                }
            }
            
            logger.info(f"Task executed successfully: {task_data.get('task_id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing task: {str(e)}")
            return self._get_error_response(task_data, message, str(e))
    
    async def _call_idit_api(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call IDIT API with task data"""
        try:
            execution_params = task_data.get('execution_params', {})
            ivo_json = task_data.get('ivo_json', {})
            
            # Make API call through IDIT client
            response = await self.idit_client.execute_action(
                endpoint=execution_params.get('api_endpoint'),
                method=execution_params.get('http_method', 'POST'),
                data=ivo_json,
                timeout=execution_params.get('timeout', 30)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"IDIT API call failed: {str(e)}")
            raise
    
    async def _generate_user_response(
        self, 
        task_data: Dict[str, Any], 
        api_response: Dict[str, Any],
        message: Dict[str, Any]
    ) -> str:
        """Generate user-friendly response using LLM"""
        try:
            # Create response generation task
            task = Task(
                description=self._build_response_prompt(task_data, api_response, message),
                agent=self.agent,
                expected_output="""A clear, concise, and friendly message to send back to the user.
                The message should:
                1. Acknowledge their request
                2. Provide the result or status
                3. Include relevant details (confirmation numbers, next steps, etc.)
                4. Be appropriate for the channel (formal for email, casual for WhatsApp)
                5. End with helpful information or call-to-action if needed"""
            )
            
            # Execute response generation
            response_text = task.execute()
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating user response: {str(e)}")
            return self._get_fallback_response(task_data, api_response)
    
    def _build_response_prompt(
        self,
        task_data: Dict[str, Any],
        api_response: Dict[str, Any],
        message: Dict[str, Any]
    ) -> str:
        """Build the response generation prompt for the LLM"""
        return f"""
        Generate a user-friendly response message based on the task execution results.
        
        Task Information:
        - Task ID: {task_data.get('task_id')}
        - Action Type: {task_data.get('action_type')}
        
        API Response:
        - Success: {api_response.get('success')}
        - Status Code: {api_response.get('status_code')}
        - Response Data: {api_response.get('data')}
        - Message: {api_response.get('message')}
        
        Original Message Context:
        - Channel: {message.get('channel')}
        - User Request: {message.get('content')}
        
        Response Guidelines:
        1. Be clear and professional
        2. Match the tone to the channel (formal for email, friendly for WhatsApp/Teams)
        3. Include specific details from the API response (IDs, dates, amounts)
        4. If successful, confirm what was done and provide next steps
        5. If failed, explain the issue and suggest alternatives
        6. Keep it concise but informative
        7. End with a helpful closing or call-to-action
        
        Generate the response message now.
        """
    
    def _get_fallback_response(self, task_data: Dict[str, Any], api_response: Dict[str, Any]) -> str:
        """Provide fallback response if LLM fails"""
        action_type = task_data.get('action_type', 'request')
        
        if api_response.get('success'):
            return f"""Your {action_type} has been processed successfully. 
            Reference ID: {task_data.get('task_id')}
            
            We'll get back to you shortly with more details."""
        else:
            return f"""We encountered an issue processing your {action_type}. 
            Our team has been notified and will assist you shortly.
            Reference ID: {task_data.get('task_id')}"""
    
    def _get_error_response(
        self, 
        task_data: Dict[str, Any], 
        message: Dict[str, Any], 
        error: str
    ) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "execution_status": "failed",
            "api_response": {
                "success": False,
                "error": error,
                "status_code": 500
            },
            "user_response": f"""We're sorry, but we couldn't process your request at this time. 
            Our technical team has been notified. Please try again later or contact support.
            Reference ID: {task_data.get('task_id')}""",
            "metadata": {
                "task_id": task_data.get('task_id'),
                "action_type": task_data.get('action_type'),
                "channel": message.get('channel'),
                "error": error
            }
        }


# Singleton instance
_task_execution_agent = None

def get_task_execution_agent() -> TaskExecutionAgent:
    """Get or create task execution agent singleton"""
    global _task_execution_agent
    if _task_execution_agent is None:
        _task_execution_agent = TaskExecutionAgent()
    return _task_execution_agent
