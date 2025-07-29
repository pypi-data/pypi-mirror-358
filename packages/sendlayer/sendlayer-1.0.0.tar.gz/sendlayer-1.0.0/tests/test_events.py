import pytest
from datetime import datetime, timedelta
from sendlayer import SendLayer
from sendlayer.exceptions import SendLayerValidationError

def test_get_events(events_client):
    start_date = datetime.now() - timedelta(days=1)
    end_date = datetime.now()
    
    response = events_client.Events.get()
    
    assert isinstance(response, dict)
    assert "events" in response
    assert "totalRecords" in response
    assert isinstance(response["events"], list)
    assert len(response["events"]) > 0
    assert response["events"][0]["EventType"] == "opened"
    assert response["events"][0]["MessageID"] == "test-message-id"

def test_get_events_with_filters(events_client):
    start_date = datetime.now() - timedelta(days=1)
    
    response = events_client.Events.get(
        event="opened"
    )
    
    assert isinstance(response, dict)
    assert "events" in response
    assert isinstance(response["events"], list)
    assert len(response["events"]) > 0
    assert response["events"][0]["EventType"] == "opened"


def test_get_events_validation(events_client):
    # Test invalid event type
    with pytest.raises(SendLayerValidationError, match="Error: Invalid event name - 'invalid' is not a valid event name"):
        events_client.Events.get(event="invalid")
    
    # Test invalid date range
    with pytest.raises(SendLayerValidationError, match="Error: Invalid date range - End date must be after start date"):
        events_client.Events.get(
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(days=1)
        )
    
    # Test invalid retrieve_count
    with pytest.raises(SendLayerValidationError, match="Error: Invalid retrieve count - must be between 1 and 100"):
        events_client.Events.get(retrieve_count=0)
    
    with pytest.raises(SendLayerValidationError, match="Error: Invalid retrieve count - must be between 1 and 100"):
        events_client.Events.get(retrieve_count=101)