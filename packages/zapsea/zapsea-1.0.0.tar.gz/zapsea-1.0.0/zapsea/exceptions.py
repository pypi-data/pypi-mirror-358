"""
ZapSEA Python SDK - Exception Classes

Defines all exception types that can be raised by the ZapSEA SDK.
"""

from typing import Optional, Dict, Any


class ZapSEAError(Exception):
    """
    Base exception class for all ZapSEA SDK errors.
    
    All other ZapSEA exceptions inherit from this class.
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
    
    def __str__(self) -> str:
        if self.status_code:
            return f"ZapSEA API Error ({self.status_code}): {self.message}"
        return f"ZapSEA SDK Error: {self.message}"


class AuthenticationError(ZapSEAError):
    """
    Raised when API authentication fails.
    
    This typically indicates:
    - Invalid API key
    - Expired API key
    - Missing Authorization header
    - Malformed API key format
    """
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class RateLimitError(ZapSEAError):
    """
    Raised when API rate limits are exceeded.
    
    Different tiers have different rate limits:
    - Free: 60 requests/minute
    - Professional: 300 requests/minute  
    - Enterprise: 1000 requests/minute
    """
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg} (retry after {self.retry_after} seconds)"
        return base_msg


class ValidationError(ZapSEAError):
    """
    Raised when request validation fails.
    
    This indicates issues with request parameters such as:
    - Missing required fields
    - Invalid field values
    - Malformed request structure
    - Type mismatches
    """
    
    def __init__(self, message: str, validation_errors: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422)
        self.validation_errors = validation_errors or {}
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.validation_errors:
            error_details = ", ".join([f"{field}: {error}" for field, error in self.validation_errors.items()])
            return f"{base_msg} - Details: {error_details}"
        return base_msg


class APIError(ZapSEAError):
    """
    Raised for general API errors.
    
    This covers various API-level errors including:
    - Server errors (5xx)
    - Client errors (4xx) not covered by specific exceptions
    - Unexpected response formats
    - Service unavailable
    """
    
    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        super().__init__(message, status_code=status_code)
        self.error_code = error_code
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.error_code:
            return f"{base_msg} (error code: {self.error_code})"
        return base_msg


class JobTimeoutError(ZapSEAError):
    """
    Raised when an async job doesn't complete within the specified timeout.
    
    This can happen when:
    - Complex simulations take longer than expected
    - API is experiencing high load
    - Network connectivity issues
    - Job is stuck in processing state
    """
    
    def __init__(self, message: str, job_id: Optional[str] = None, timeout_seconds: Optional[int] = None):
        super().__init__(message)
        self.job_id = job_id
        self.timeout_seconds = timeout_seconds
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.job_id and self.timeout_seconds:
            return f"{base_msg} (job: {self.job_id}, timeout: {self.timeout_seconds}s)"
        elif self.job_id:
            return f"{base_msg} (job: {self.job_id})"
        return base_msg


class NetworkError(ZapSEAError):
    """
    Raised when network-level errors occur.
    
    This includes:
    - Connection timeouts
    - DNS resolution failures
    - SSL/TLS errors
    - Network unreachable
    """
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.original_error:
            return f"{base_msg} (caused by: {self.original_error})"
        return base_msg


class ConfigurationError(ZapSEAError):
    """
    Raised when SDK configuration is invalid.
    
    This includes:
    - Invalid base URL format
    - Missing required configuration
    - Invalid timeout values
    - Malformed API key
    """
    
    def __init__(self, message: str, config_field: Optional[str] = None):
        super().__init__(message)
        self.config_field = config_field
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.config_field:
            return f"{base_msg} (field: {self.config_field})"
        return base_msg


class ResourceNotFoundError(ZapSEAError):
    """
    Raised when a requested resource is not found.
    
    This includes:
    - Job ID not found
    - Policy ID not found
    - Entity ID not found
    - User not found
    """
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        super().__init__(message, status_code=404)
        self.resource_type = resource_type
        self.resource_id = resource_id
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.resource_type and self.resource_id:
            return f"{base_msg} ({self.resource_type}: {self.resource_id})"
        elif self.resource_type:
            return f"{base_msg} (resource type: {self.resource_type})"
        return base_msg


class QuotaExceededError(ZapSEAError):
    """
    Raised when usage quotas are exceeded.
    
    This includes:
    - Monthly API call limits
    - Storage quotas
    - Feature usage limits
    """
    
    def __init__(self, message: str, quota_type: Optional[str] = None, current_usage: Optional[int] = None, limit: Optional[int] = None):
        super().__init__(message, status_code=402)
        self.quota_type = quota_type
        self.current_usage = current_usage
        self.limit = limit
    
    def __str__(self) -> str:
        base_msg = super().__str__()
        if self.quota_type and self.current_usage and self.limit:
            return f"{base_msg} ({self.quota_type}: {self.current_usage}/{self.limit})"
        elif self.quota_type:
            return f"{base_msg} (quota: {self.quota_type})"
        return base_msg
