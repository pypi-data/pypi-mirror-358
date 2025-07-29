<a href="https://sendlayer.com">
<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-dark.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-light.svg">
  <img alt="SendLayer Logo" width="200px" src="https://sendlayer.com/wp-content/themes/sendlayer-theme/assets/images/svg/logo-light.svg">
</picture>
</a>

### SendLayer Python SDK

The official Python SDK for interacting with the SendLayer API, providing a simple and intuitive interface for sending emails, managing webhooks, and retrieving email events.

[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)


## Installation

```bash
pip install sendlayer
```

## Quick Start

```python
from sendlayer import SendLayer

# Initialize the email client with your API key
sendlayer = SendLayer("your-api-key")

# Send an email
response = sendlayer.Emails.send(
    sender="sender@example.com",
    to="recipient@example.com",
    subject="Test Email",
    text="This is a test email"
)
```

## Features

- **Email Module**: Send emails with support for HTML/text content, attachments, CC/BCC, and templates
- **Webhooks Module**: Create, retrieve, and delete webhooks for various email events
- **Events Module**: Retrieve email events with filtering options
- **Error Handling**: Custom exceptions for better error management
- **Type Hints**: Full type support for better IDE integration

## Documentation

### Email Module

Send emails using the `SendLayer` module:

```python
from sendlayer import SendLayer

sendlayer = SendLayer(api_key='your-api-key')


# Send a complex email
response = sendlayer.Emails.send(
    sender={"email": "sender@example.com", "name": "Paulie Paloma"},
    to=[
        {'email': 'recipient1@example.com', 'name': 'Recipient 1'},
        {'email': 'recipient2@example.com', 'name': 'Recipient 2'}
    ],
    subject='Complex Email',
    html='<p>This is a <strong>test email</strong>!</p>',
    text='This is a test email!',
    cc=[{'email': 'cc@example.com', 'name': 'CC Recipient'}],
    bcc=[{'email': 'bcc@example.com', 'name': 'BCC Recipient'}],
    reply_to=[{'email': 'reply@example.com', 'name': 'Reply To'}],
    attachments=[{
        'path': 'path/to/file.pdf',
        'type': 'application/pdf',
    }]
)
```

### Webhooks Module

```python
from sendlayer import SendLayer

sendlayer = SendLayer(api_key='your-api-key')

# Create a webhook
# Webhook event options: bounce, click, open, unsubscribe, complaint, delivery

webhook = sendlayer.Webhooks.create(
    url='https://your-domain.com/webhook',
    event='open'
)

# Get all webhooks
webhooks = sendlayer.Webhooks.get()

# Delete a webhook
sendlayer.Webhooks.delete(webhook_id=123)
```

### Events Module

```python
from sendlayer import SendLayer
from datetime import datetime, timedelta

sendlayer = SendLayer(api_key='your-api-key')

# Get all events
events = sendlayer.Events.get()

# Get filtered events
events = sendlayer.Events.get(
    start_date=datetime.now() - timedelta(hours=4),
    end_date=datetime.now(),
    event='opened'
)
```

## Error Handling

The SDK provides custom exceptions for better error handling:

```python
from sendlayer import (
    SendLayerError,
    SendLayerAPIError,
)

try:
    response = sendlayer.Emails.send(...)
except SendLayerError as e:
    print(f"API error: {e.status_code} - {e.message}")
except SendLayerError:
    print("An unexpected error occurred")
```

## More Details
To learn more about using the SendLayer SDK, be sure to check our [Developer Documentation](https://developers.sendlayer.com/sdks/python).


## License

MIT License - see [LICENSE](./LICENSE) file for details 