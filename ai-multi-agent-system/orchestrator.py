"""
Orchestrator
Main orchestration engine that coordinates all agents and services
"""
import asyncio
from typing import Dict, Any, List
from agents import get_classification_agent, get_task_creation_agent, get_task_execution_agent
from services import get_message_pull_service
from utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


class Orchestrator:
    """
    Main orchestrator for the AI Multi-Agent System
    Coordinates message flow through classification, task creation, and execution
    """
    
    def __init__(self):
        self.classification_agent = get_classification_agent()
        self.task_creation_agent = get_task_creation_agent()
        self.task_execution_agent = get_task_execution_agent()
        self.message_service = get_message_pull_service()
        self.max_concurrent_tasks = settings.app.max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(self.max_concurrent_tasks)
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single message through the full pipeline
        
        Args:
            message: Standardized message dictionary
        
        Returns:
            Processing result with status and response
        """
        async with self.semaphore:
            try:
                logger.info(f"Processing message {message.get('message_id')} from {message.get('channel')}")
                
                # Stage 1: Classification
                classification_result = await self._classify_message(message)
                
                if not classification_result:
                    logger.error("Classification failed")
                    return self._create_error_result(message, "Classification failed")
                
                # Stage 2: Task Creation
                task_data = await self._create_task(classification_result, message)
                
                if not task_data:
                    logger.error("Task creation failed")
                    return self._create_error_result(message, "Task creation failed")
                
                # Stage 3: Task Execution
                execution_result = await self._execute_task(task_data, message)
                
                # Stage 4: Send Response
                response_sent = await self._send_response(execution_result, message)
                
                # Compile final result
                result = {
                    "status": "success" if execution_result.get("execution_status") == "success" else "failed",
                    "message_id": message.get('message_id'),
                    "channel": message.get('channel'),
                    "classification": classification_result,
                    "task": task_data,
                    "execution": execution_result,
                    "response_sent": response_sent
                }
                
                logger.info(f"Message {message.get('message_id')} processed successfully")
                return result
                
            except Exception as e:
                logger.error(f"Error processing message {message.get('message_id')}: {str(e)}")
                return self._create_error_result(message, str(e))
    
    async def process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple messages concurrently
        
        Args:
            messages: List of standardized messages
        
        Returns:
            List of processing results
        """
        logger.info(f"Processing {len(messages)} messages")
        
        tasks = [self.process_message(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing message {idx}: {str(result)}")
                processed_results.append(self._create_error_result(messages[idx], str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _classify_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Run message through classification agent"""
        try:
            logger.info(f"Classifying message {message.get('message_id')}")
            
            # Run classification in executor to avoid blocking
            loop = asyncio.get_event_loop()
            classification = await loop.run_in_executor(
                None,
                self.classification_agent.classify_message,
                message
            )
            
            return classification
            
        except Exception as e:
            logger.error(f"Classification error: {str(e)}")
            return None
    
    async def _create_task(self, classification: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """Create task from classification result"""
        try:
            logger.info(f"Creating task for action_id: {classification.get('action_id')}")
            
            # Run task creation in executor
            loop = asyncio.get_event_loop()
            task_data = await loop.run_in_executor(
                None,
                self.task_creation_agent.create_task,
                classification,
                message
            )
            
            return task_data
            
        except Exception as e:
            logger.error(f"Task creation error: {str(e)}")
            return None
    
    async def _execute_task(self, task_data: Dict[str, Any], message: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task via IDIT API"""
        try:
            logger.info(f"Executing task {task_data.get('task_id')}")
            
            execution_result = await self.task_execution_agent.execute_task(task_data, message)
            
            return execution_result
            
        except Exception as e:
            logger.error(f"Task execution error: {str(e)}")
            return {
                "execution_status": "failed",
                "error": str(e),
                "user_response": "An error occurred while processing your request."
            }
    
    async def _send_response(self, execution_result: Dict[str, Any], message: Dict[str, Any]) -> bool:
        """Send response back to user via appropriate channel"""
        try:
            channel = message.get('channel')
            sender = message.get('sender')
            response_text = execution_result.get('user_response', 'Your request has been processed.')
            
            # Prepare metadata based on channel
            metadata = {}
            if channel == 'email':
                original_subject = message.get('metadata', {}).get('subject', '')
                metadata['subject'] = f"Re: {original_subject}" if original_subject else "Response to your inquiry"
            elif channel == 'teams':
                metadata['title'] = "Task Update"
                metadata['type'] = 'success' if execution_result.get('execution_status') == 'success' else 'error'
            
            # Send response
            success = await self.message_service.send_response(
                channel=channel,
                recipient=sender,
                content=response_text,
                metadata=metadata
            )
            
            if success:
                logger.info(f"Response sent successfully to {sender} via {channel}")
            else:
                logger.warning(f"Failed to send response to {sender} via {channel}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending response: {str(e)}")
            return False
    
    def _create_error_result(self, message: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            "status": "error",
            "message_id": message.get('message_id'),
            "channel": message.get('channel'),
            "error": error,
            "classification": None,
            "task": None,
            "execution": None,
            "response_sent": False
        }
    
    async def start(self):
        """Start the orchestrator in polling mode"""
        logger.info("Starting AI Multi-Agent Orchestration System")
        
        try:
            # Start message polling with callback
            await self.message_service.start_polling(self.process_messages)
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
            self.stop()
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}")
            raise
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping AI Multi-Agent Orchestration System")
        self.message_service.stop_polling()


# Singleton instance
_orchestrator = None

def get_orchestrator() -> Orchestrator:
    """Get or create orchestrator singleton"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
