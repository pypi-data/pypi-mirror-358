"""
ZapSEA Python SDK - Authentication

Handles API key authentication for ZapSEA API requests.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """
    API Key authentication handler for ZapSEA API.
    
    Handles Bearer token authentication using ZapSEA API keys.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize API key authentication.
        
        Args:
            api_key: ZapSEA API key (starts with 'pk_live_' or 'pk_test_')
            
        Raises:
            ValueError: Invalid API key format
        """
        
        if not api_key:
            raise ValueError("API key is required")
        
        if not isinstance(api_key, str):
            raise ValueError("API key must be a string")
        
        if not api_key.startswith(("pk_live_", "pk_test_")):
            raise ValueError("Invalid API key format. Must start with 'pk_live_' or 'pk_test_'")
        
        self.api_key = api_key
        self.is_test_key = api_key.startswith("pk_test_")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary with Authorization header
        """
        
        return {
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def is_valid_format(self) -> bool:
        """
        Check if the API key has a valid format.
        
        Returns:
            True if format is valid, False otherwise
        """
        
        if not self.api_key:
            return False
        
        # Check prefix
        if not self.api_key.startswith(("pk_live_", "pk_test_")):
            return False
        
        # Check length (prefix + 32 character key)
        if len(self.api_key) != 39:  # 7 (prefix) + 32 (key) = 39
            return False
        
        # Check that key part contains only alphanumeric characters
        key_part = self.api_key[7:]  # Remove prefix
        if not key_part.isalnum():
            return False
        
        return True
    
    def get_key_info(self) -> Dict[str, Any]:
        """
        Get information about the API key.
        
        Returns:
            Dictionary with key information
        """
        
        return {
            "key_prefix": self.api_key[:12] + "...",  # Show first 12 characters
            "is_test_key": self.is_test_key,
            "is_live_key": not self.is_test_key,
            "is_valid_format": self.is_valid_format()
        }
    
    def __repr__(self) -> str:
        """String representation of the auth handler."""
        key_type = "test" if self.is_test_key else "live"
        return f"APIKeyAuth(key_type='{key_type}', prefix='{self.api_key[:12]}...')"
