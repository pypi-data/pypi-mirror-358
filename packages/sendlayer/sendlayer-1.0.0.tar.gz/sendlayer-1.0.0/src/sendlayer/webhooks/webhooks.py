from typing import List, Dict, Any
import re
from sendlayer.base import BaseClient
from sendlayer.exceptions import SendLayerValidationError

class Webhooks:
    """Client for managing webhooks in SendLayer."""

    def __init__(self, client: BaseClient):
        self.client = client
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
        return bool(re.match(pattern, url))
    
    def create(self, url: str, event: str) -> Dict[str, int]:
        """Create a new webhook."""
        if not self._validate_url(url):
            raise SendLayerValidationError(f"Error: Invalid webhook URL - {url}")
            
        payload = {
            "WebhookURL": url,
            "Event": event
        }

        event_options = ["bounce", "click", "open", "unsubscribe", "complaint", "delivery"]

        # Validate event name
        if event not in event_options:
            raise SendLayerValidationError(f"Error: '{event}' is not a valid event name. Supported events include {event_options}")

        return self.client._make_request("POST", "webhooks", json=payload)
    
    def get(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all webhooks."""
        response = self.client._make_request("GET", "webhooks")
        return response
    
    def delete(self, webhook_id: int) -> None:
        """Delete a webhook by ID."""
        
        # Validate webhook_id
        if not isinstance(webhook_id, int):
            raise SendLayerValidationError("WebhookID must be an integer")
        
        if webhook_id <= 0:
            raise SendLayerValidationError("WebhookID must be greater than 0")
        
        return self.client._make_request("DELETE", f"webhooks/{webhook_id}") 