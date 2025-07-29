"""SendLayer Python SDK."""

from .base import BaseClient
from .email import Emails
from .webhooks import Webhooks
from .events import Events
from .exceptions import (
    SendLayerError,
    SendLayerAPIError,
)

class SendLayer:
    def __init__(self, api_key: str):
        client = BaseClient(api_key)
        self.Emails = Emails(client)
        self.Webhooks = Webhooks(client)
        self.Events = Events(client)

__all__ = [
    "SendLayer",
    "SendLayerError",
    "SendLayerAPIError",
] 