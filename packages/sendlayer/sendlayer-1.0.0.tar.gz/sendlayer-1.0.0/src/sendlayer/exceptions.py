class SendLayerError(Exception):
    """Base exception for SendLayer SDK."""
    pass

class SendLayerAPIError(SendLayerError):
    """Exception raised for API errors."""
    def __init__(self, message: str, status_code: int, response: dict):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(f"API Error {status_code}: {message}")

class SendLayerAuthenticationError(SendLayerError):
    """Exception raised for authentication errors."""
    pass

class SendLayerNotFoundError(SendLayerError):
    """Exception raised for not found errors."""
    pass

class SendLayerRateLimitError(SendLayerError):
    """Exception raised for rate limit errors."""
    pass

class SendLayerValidationError(SendLayerError):
    """Exception raised for validation errors."""
    pass 

class SendLayerInternalServerError(SendLayerError):
    """Exception raised for internal server errors."""
    pass