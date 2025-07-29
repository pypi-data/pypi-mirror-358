import requests
from typing import Dict, Any, Optional
from ..exceptions import (
    SendLayerError,
    SendLayerAPIError,
    SendLayerAuthenticationError,
    SendLayerValidationError,
    SendLayerNotFoundError,
    SendLayerRateLimitError,
    SendLayerInternalServerError
)

class BaseClient:
    """Base client for SendLayer API interactions."""
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the base client with API key and optional configuration."""
        self.api_key = api_key
        self.base_url = "https://console.sendlayer.com/api/v1"
        
        # Set default config values
        config = config or {}
        self.attachment_url_timeout = config.get('attachmentURLTimeout', 30000)
        
        # Configure session
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # Apply any additional session configuration from config
        if 'requests' in config:
            requests_config = config['requests']
            if 'timeout' in requests_config:
                self._session.timeout = requests_config['timeout']
            if 'headers' in requests_config:
                self._session.headers.update(requests_config['headers'])

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the SendLayer API."""
        url = f"{self.base_url}/{endpoint}"
        response = self._session.request(method, url, **kwargs)
        
        if not response.ok:
            if response.status_code == 401:
                raise SendLayerAuthenticationError("401: Invalid API key")
            elif response.status_code == 400:
                raise SendLayerValidationError(response.json().get("Error", "400: Invalid request parameters"))
            elif response.status_code == 404:
                raise SendLayerNotFoundError(response.json().get("Error", "404: Resource not found"))
            elif response.status_code == 429:
                raise SendLayerRateLimitError(response.json().get("Error", "429: Rate limit exceeded"))
            elif response.status_code == 500:
                raise SendLayerInternalServerError(response.json().get("Error", "500: Internal server error"))
            elif response.status_code == 422:
                raise SendLayerValidationError(response.json().get("Error", "422: Invalid request parameters"))
            else:
                try:
                    response_data = response.json()
                except:
                    response_data = {"error": response.text}
                raise SendLayerAPIError(
                    message=response_data.get("Error", "API error"),
                    status_code=response.status_code,
                    response=response_data
                )
        
        return response.json() 