"""
AgentMeter SDK Exception Classes
"""


class AgentMeterError(Exception):
    """Base exception class for AgentMeter SDK errors."""
    
    def __init__(self, message: str, error_code: str = None, **kwargs):
        self.error_code = error_code
        self.extra_data = kwargs
        super().__init__(message)


class AgentMeterAPIError(AgentMeterError):
    """Exception raised when the AgentMeter API returns an error."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(message)


class AgentMeterValidationError(AgentMeterError):
    """Exception raised when input validation fails."""
    pass


class AgentMeterConfigurationError(AgentMeterError):
    """Exception raised when there are configuration issues."""
    pass


class AgentMeterConnectionError(AgentMeterError):
    """Exception raised when there are connection issues with the API."""
    pass


class RateLimitError(AgentMeterAPIError):
    """Exception raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(message, status_code=429)