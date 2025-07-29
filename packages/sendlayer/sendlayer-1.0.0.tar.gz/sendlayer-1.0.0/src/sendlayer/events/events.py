from datetime import datetime
from typing import List, Dict, Optional, Any
from sendlayer.base import BaseClient
from sendlayer.exceptions import SendLayerValidationError


class Events:
    """Client for retrieving email events from SendLayer."""

    def __init__(self, client: BaseClient):
        self.client = client
    
    def get(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event: Optional[str] = None,
        message_id: Optional[str] = None,
        start_from: Optional[int] = None,
        retrieve_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get email events from SendLayer
        
        Args:
            start_date (Optional[datetime]): Start date for filtering
            end_date (Optional[datetime]): End date for filtering
            event (Optional[str]): Event type filter
            message_id (Optional[str]): Specific message ID to filter
            start_from (Optional[int]): Starting index
            retrieve_count (Optional[int]): Number of records to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of events
        """

        event_options = ["accepted", "rejected", "delivered", "opened", "clicked", "unsubscribed", "complained", "failed"]
        params = {}
        
        # Validate date range
        if start_date and end_date and end_date <= start_date:
            raise SendLayerValidationError("Error: Invalid date range - End date must be after start date")
            
        if start_date:
            params["StartDate"] = int(start_date.timestamp())
        if end_date:
            params["EndDate"] = int(end_date.timestamp())
            
        if event:
            # Validate event name
            if event not in event_options:
                raise SendLayerValidationError(f"Error: Invalid event name - '{event}' is not a valid event name")
            params["Event"] = event

        if message_id:
            params["MessageID"] = message_id
        if start_from is not None:
            params["StartFrom"] = start_from
        if retrieve_count is not None:
            if retrieve_count <= 0 or retrieve_count > 100:
                raise SendLayerValidationError("Error: Invalid retrieve count - must be between 1 and 100")
            params["RetrieveCount"] = retrieve_count
            
        response = self.client._make_request("GET", "events", params=params)
        events =  response.get('Events', [])
        total_records = response.get('TotalRecords', 0)

        return {
                "totalRecords": total_records, 
                "events": events
            }