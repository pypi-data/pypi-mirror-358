class APALError(Exception):
    """Base exception for all APAL client errors"""
    pass

class ValidationError(APALError):
    """Raised when message validation fails"""
    pass

class AuthenticationError(APALError):
    """Raised when authentication fails"""
    pass

class MessageError(APALError):
    """Raised when message processing fails"""
    pass

class APIError(APALError):
    """Raised when API request fails"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}") 