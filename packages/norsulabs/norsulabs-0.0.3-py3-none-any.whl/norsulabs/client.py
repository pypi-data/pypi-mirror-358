import requests
from requests import Session, Request, Response
from typing import Dict, Any
import time

class NorsuLabsAPIError(Exception):
    def __init__(self, status_code: int, message: str, response_text: str = ""):
        self.status_code = status_code
        self.message = message
        self.response_text = response_text
        super().__init__(f"API Error {status_code}: {message}")

class NorsuLabsClient:
    def __init__(self, api_key: str, deployment_id: int, base_url: str = "https://deployments.norsulabs.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.deployment_id = deployment_id
        self.session = Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })

    def inference(self, request_data: Dict[str, Any], timeout: int = 30, max_retries: int = 3) -> Dict[str, Any]:
        """
        Make an inference request to the NorsuLabs API
        
        Args:
            request_data: The request payload
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict containing the API response
            
        Raises:
            NorsuLabsAPIError: For API-related errors
            requests.RequestException: For network-related errors
        """
        payload = {
            "deployment_id": self.deployment_id,
            "request": request_data
        }
        
        for attempt in range(max_retries + 1):
            try:
                response = self.session.post(
                    url=f"{self.base_url}/",
                    json=payload,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError as e:
                        raise NorsuLabsAPIError(200, "Invalid JSON response", response.text)
                
                if response.status_code == 401:
                    raise NorsuLabsAPIError(401, "Unauthorized - check your API key", response.text)
                elif response.status_code == 404:
                    raise NorsuLabsAPIError(404, "Deployment not found", response.text)
                elif response.status_code == 429:
                    raise NorsuLabsAPIError(429, "Too many requests - rate limit exceeded. Upgrade your plan for higher limits.", response.text)
                elif response.status_code >= 500:
                    if attempt < max_retries:
                        time.sleep(2 ** attempt)  
                        continue
                    raise NorsuLabsAPIError(response.status_code, "Server error", response.text)
                else:
                    raise NorsuLabsAPIError(response.status_code, "Request failed", response.text)
                    
            except requests.RequestException as e:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                raise
                
        raise NorsuLabsAPIError(500, "Max retries exceeded")