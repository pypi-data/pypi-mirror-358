import pytest
import os
from sendlayer import SendLayer
from sendlayer.exceptions import SendLayerValidationError

def test_send_simple_email(email_client):
    response = email_client.Emails.send(
        to="recipient@example.com",
        sender="sender@example.com",
        subject="Test Email",
        text="This is a test email"
    )
    assert response["MessageID"] == "test-message-id"

def test_send_complex_email(email_client):
    response = email_client.Emails.send(
        to=[{"email": "recipient1@example.com", "name": "Recipient 1"}, "recipient2@example.com"],
        sender={"email": "sender@example.com", "name": "Sender Name"},
        subject="Complex Email",
        html="<p>This is a test email</p>",
        text="This is a test email",
        cc=[{"email": "cc@example.com", "name": "CC Recipient"}],
        bcc=[{"email": "bcc@example.com", "name": "BCC Recipient"}],
        reply_to={"email": "reply@example.com", "name": "Reply To"},
        attachments=[{"path": "./test_attachment.txt", "type": "text/plain"}],
        headers={"X-Custom-Header": "value"},
        tags=["tag1", "tag2"]
    )
    assert response["MessageID"] == "test-message-id"

def test_send_email_validation(email_client):
    # Test invalid sender email
    with pytest.raises(SendLayerValidationError, match="Invalid sender email address"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="invalid-email",
            subject="Test",
            text="Test email content"
        )
    
    # Test invalid recipient email
    with pytest.raises(SendLayerValidationError, match="Invalid recipient email address"):
        email_client.Emails.send(
            to="invalid-email",
            sender="sender@example.com",
            subject="Test",
            text="Test email content"
        )
    
    # Test invalid cc email
    with pytest.raises(SendLayerValidationError, match="Invalid cc email address"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="sender@example.com",
            subject="Test",
            text="Test email content",
            cc=["invalid-email"]
        )
    
    # Test invalid bcc email
    with pytest.raises(SendLayerValidationError, match="Invalid bcc email address"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="sender@example.com",
            subject="Test",
            text="Test email content",
            bcc=["invalid-email"]
        )
    
    # Test invalid reply_to email
    with pytest.raises(SendLayerValidationError, match="Invalid reply_to email address"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="sender@example.com",
            subject="Test",
            text="Test email content",
            reply_to="invalid-email"
        )
    
    # Test invalid attachment path
    with pytest.raises(SendLayerValidationError, match="Attachment path is required"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="sender@example.com",
            subject="Test",
            text="Test email content",
            attachments=[{"type": "text/plain"}]
        )

    # Test missing attachment type
    with pytest.raises(SendLayerValidationError, match="Attachment type is required"):
        email_client.Emails.send(
            to="recipient@example.com",
            sender="sender@example.com",
            subject="Test",
            text="Test email content",
            attachments=[{"path": "./test.txt"}]
        ) 