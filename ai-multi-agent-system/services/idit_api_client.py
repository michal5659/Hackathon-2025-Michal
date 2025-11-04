"""
IDIT API Client
Handles all communications with the IDIT external API
"""
import httpx
from typing import Dict, Any, Optional
from config.settings import settings
from utils.logger import get_logger
import time

logger = get_logger(__name__)


class IDITAPIClient:
    """Client for IDIT API integration"""
    
    def __init__(self):
        self.base_url = settings.idit_api.base_url
        self.api_key = settings.idit_api.api_key
        self.timeout = settings.idit_api.timeout
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'AI-Multi-Agent-System/1.0'
        }
    
    async def execute_action(
        self, 
        endpoint: str, 
        method: str = 'POST',
        data: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute an action via IDIT API
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request payload
            timeout: Request timeout in seconds
        
        Returns:
            Dict containing:
                - success: Boolean indicating success
                - status_code: HTTP status code
                - data: Response data
                - message: Response message
                - execution_time: Time taken for request
        """
        start_time = time.time()
        
        try:
            logger.info(f"Calling IDIT API: {method} {endpoint}")
            
            url = f"{self.base_url}{endpoint}"
            request_timeout = timeout or self.timeout
            
            async with httpx.AsyncClient() as client:
                if method.upper() == 'GET':
                    response = await client.get(
                        url,
                        headers=self.headers,
                        params=data,
                        timeout=request_timeout
                    )
                elif method.upper() == 'POST':
                    response = await client.post(
                        url,
                        headers=self.headers,
                        json=data,
                        timeout=request_timeout
                    )
                elif method.upper() == 'PUT':
                    response = await client.put(
                        url,
                        headers=self.headers,
                        json=data,
                        timeout=request_timeout
                    )
                elif method.upper() == 'DELETE':
                    response = await client.delete(
                        url,
                        headers=self.headers,
                        timeout=request_timeout
                    )
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                execution_time = time.time() - start_time
                
                # Parse response
                result = self._parse_response(response, execution_time)
                
                logger.info(f"IDIT API call completed: {result['success']} (took {execution_time:.2f}s)")
                return result
                
        except httpx.TimeoutException as e:
            logger.error(f"IDIT API timeout: {str(e)}")
            return self._create_error_response("Request timeout", 408, time.time() - start_time)
        except httpx.RequestError as e:
            logger.error(f"IDIT API request error: {str(e)}")
            return self._create_error_response(str(e), 500, time.time() - start_time)
        except Exception as e:
            logger.error(f"IDIT API unexpected error: {str(e)}")
            return self._create_error_response(str(e), 500, time.time() - start_time)
    
    def _parse_response(self, response: httpx.Response, execution_time: float) -> Dict[str, Any]:
        """Parse HTTP response into standardized format"""
        try:
            response_data = response.json() if response.text else {}
        except:
            response_data = {"raw_response": response.text}
        
        success = 200 <= response.status_code < 300
        
        return {
            "success": success,
            "status_code": response.status_code,
            "data": response_data,
            "message": response_data.get('message', response.reason_phrase) if success else f"Error: {response.reason_phrase}",
            "execution_time": execution_time
        }
    
    def _create_error_response(self, error_message: str, status_code: int, execution_time: float) -> Dict[str, Any]:
        """Create standardized error response"""
        return {
            "success": False,
            "status_code": status_code,
            "data": {},
            "message": error_message,
            "execution_time": execution_time
        }
    
    async def health_check(self) -> bool:
        """Check IDIT API health"""
        try:
            result = await self.execute_action("/health", method="GET")
            return result["success"]
        except Exception as e:
            logger.error(f"IDIT API health check failed: {str(e)}")
            return False
    
    async def submit_policy_inquiry(self, customer_id: str, policy_number: str, inquiry_details: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a policy inquiry"""
        data = {
            "customer_id": customer_id,
            "policy_number": policy_number,
            "inquiry_type": inquiry_details.get("type", "general"),
            "details": inquiry_details
        }
        return await self.execute_action("/api/v1/policies/inquiry", data=data)
    
    async def submit_claim(self, customer_id: str, policy_number: str, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new claim"""
        data = {
            "customer_id": customer_id,
            "policy_number": policy_number,
            "claim_type": claim_data.get("type"),
            "incident_date": claim_data.get("incident_date"),
            "description": claim_data.get("description"),
            "amount": claim_data.get("amount"),
            "attachments": claim_data.get("attachments", [])
        }
        return await self.execute_action("/api/v1/claims/submit", data=data)
    
    async def get_claim_status(self, claim_id: str) -> Dict[str, Any]:
        """Get claim status"""
        return await self.execute_action(f"/api/v1/claims/status/{claim_id}", method="GET")
    
    async def update_policy(self, policy_number: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update policy details"""
        data = {
            "policy_number": policy_number,
            "updates": update_data
        }
        return await self.execute_action("/api/v1/policies/update", method="PUT", data=data)
    
    async def get_payment_info(self, customer_id: str, policy_number: str) -> Dict[str, Any]:
        """Get payment information"""
        data = {
            "customer_id": customer_id,
            "policy_number": policy_number
        }
        return await self.execute_action("/api/v1/payments/inquiry", method="GET", data=data)


# Singleton instance
_idit_client = None

def get_idit_client() -> IDITAPIClient:
    """Get or create IDIT API client singleton"""
    global _idit_client
    if _idit_client is None:
        _idit_client = IDITAPIClient()
    return _idit_client
