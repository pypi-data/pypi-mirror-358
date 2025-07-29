import pytest
from sendlayer import SendLayer
from sendlayer.exceptions import SendLayerValidationError

def test_create_webhook(webhooks_client):
    response = webhooks_client.Webhooks.create("https://example.com/webhook", "open")
    assert isinstance(response, dict)
    assert "NewWebhookID" in response
    assert response["NewWebhookID"] == 123

def test_get_all_webhooks(webhooks_client):
    response = webhooks_client.Webhooks.get()
    assert isinstance(response, dict)
    assert "Webhooks" in response or "NewWebhookID" in response

def test_delete_webhook(webhooks_client):
    response = webhooks_client.Webhooks.delete(123)
    assert isinstance(response, dict)
    assert "NewWebhookID" in response or "Success" in response
    if "NewWebhookID" in response:
        assert response["NewWebhookID"] == 123

def test_create_webhook_validation(webhooks_client):
    # Test invalid URL
    with pytest.raises(SendLayerValidationError, match="Error: Invalid webhook URL"):
        webhooks_client.Webhooks.create("not-a-url", "open")
    
    # Test invalid event type
    with pytest.raises(SendLayerValidationError, match="Error: 'invalid' is not a valid event name"):
        webhooks_client.Webhooks.create("https://example.com/webhook", "invalid")

def test_delete_webhook_validation(webhooks_client):
    # Test invalid webhook_id
    with pytest.raises(SendLayerValidationError, match="WebhookID must be an integer"):
        webhooks_client.Webhooks.delete("invalid")
    # Test zero webhook_id
    with pytest.raises(SendLayerValidationError, match="WebhookID must be greater than 0"):
        webhooks_client.Webhooks.delete(0)
    # Test negative webhook_id
    with pytest.raises(SendLayerValidationError, match="WebhookID must be greater than 0"):
        webhooks_client.Webhooks.delete(-1) 