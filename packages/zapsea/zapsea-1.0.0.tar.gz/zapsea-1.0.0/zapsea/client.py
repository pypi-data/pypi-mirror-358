"""
ZapSEA Python SDK - Main Client

Provides the primary ZapSEA client class with async job polling and resource management.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import httpx

from .auth import APIKeyAuth
from .resources import Impact, Influence, Jobs, Feedback
from .exceptions import ZapSEAError, AuthenticationError, APIError
from .config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

logger = logging.getLogger(__name__)


class ZapSEA:
    """
    Main ZapSEA API client.
    
    Provides access to all ZapSEA Intelligence Engine capabilities through
    a simple, async-first interface with automatic job polling and error handling.
    
    Example:
        ```python
        client = ZapSEA(api_key="pk_live_...")
        
        # Impact simulation
        result = await client.impact.simulate(
            policy_description="AI regulation for financial services",
            analysis_depth="comprehensive"
        )
        
        # Influence pathfinding
        path = await client.influence.find_path(
            source_entity="Congress",
            target_entity="Tech Industry"
        )
        ```
    
    Args:
        api_key: Your ZapSEA API key (starts with 'pk_live_' or 'pk_test_')
        base_url: API base URL (defaults to production)
        timeout: Request timeout in seconds (default: 60)
        max_retries: Maximum number of retries for failed requests (default: 3)
        auto_poll: Whether to automatically poll for job completion (default: True)
        poll_interval: Seconds between job status polls (default: 3)
        max_poll_time: Maximum time to poll for job completion in seconds (default: 300)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_poll: bool = True,
        poll_interval: int = 3,
        max_poll_time: int = 300
    ):
        if not api_key:
            raise ValueError("API key is required")
        
        if not api_key.startswith(("pk_live_", "pk_test_")):
            raise ValueError("Invalid API key format. Must start with 'pk_live_' or 'pk_test_'")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.auto_poll = auto_poll
        self.poll_interval = poll_interval
        self.max_poll_time = max_poll_time
        
        # Initialize HTTP client with authentication
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"ZapSEA-Python-SDK/1.0.0",
                "Content-Type": "application/json"
            }
        )
        
        # Initialize resource clients
        self.impact = Impact(self)
        self.influence = Influence(self)
        self.jobs = Jobs(self)
        self.feedback = Feedback(self)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
    
    async def request(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make an authenticated HTTP request to the ZapSEA API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path (without base URL)
            json: JSON request body
            params: Query parameters
            **kwargs: Additional httpx request arguments
            
        Returns:
            Parsed JSON response
            
        Raises:
            AuthenticationError: Invalid API key or authentication failed
            RateLimitError: Rate limit exceeded
            ValidationError: Invalid request parameters
            APIError: Other API errors
            ZapSEAError: General SDK errors
        """
        
        url = f"{self.base_url}{path}"
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    **kwargs
                )
                
                # Handle different response status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202:
                    # Async job accepted
                    return response.json()
                elif response.status_code == 401:
                    raise AuthenticationError("Invalid API key or authentication failed")
                elif response.status_code == 429:
                    from .exceptions import RateLimitError
                    raise RateLimitError("Rate limit exceeded")
                elif response.status_code == 422:
                    from .exceptions import ValidationError
                    error_detail = response.json().get("detail", "Validation error")
                    raise ValidationError(f"Invalid request: {error_detail}")
                elif 400 <= response.status_code < 500:
                    error_detail = response.json().get("detail", "Client error")
                    raise APIError(f"API error ({response.status_code}): {error_detail}")
                elif 500 <= response.status_code < 600:
                    if attempt < self.max_retries:
                        # Retry on server errors
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    raise APIError(f"Server error ({response.status_code})")
                else:
                    raise APIError(f"Unexpected response status: {response.status_code}")
                    
            except httpx.RequestError as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise ZapSEAError(f"Request failed: {e}")
        
        raise ZapSEAError("Max retries exceeded")
    
    async def submit_job(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        Submit an async job and return the job ID.
        
        Args:
            method: HTTP method
            path: API endpoint path
            json: Request payload
            **kwargs: Additional request arguments
            
        Returns:
            Job ID for polling status
        """
        
        response = await self.request(method, path, json=json, **kwargs)
        
        if "job_id" not in response:
            raise APIError("Invalid job response: missing job_id")
        
        return response["job_id"]
    
    async def wait_for_job(
        self,
        job_id: str,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Poll for job completion and return the result.
        
        Args:
            job_id: Job ID to poll
            poll_interval: Seconds between polls (uses client default if None)
            max_poll_time: Maximum polling time in seconds (uses client default if None)
            
        Returns:
            Job result data
            
        Raises:
            JobTimeoutError: Job didn't complete within max_poll_time
            APIError: Job failed or other API error
        """
        
        poll_interval = poll_interval or self.poll_interval
        max_poll_time = max_poll_time or self.max_poll_time
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Check if we've exceeded max polling time
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_poll_time:
                from .exceptions import JobTimeoutError
                raise JobTimeoutError(f"Job {job_id} did not complete within {max_poll_time} seconds")
            
            # Get job status
            job_status = await self.jobs.get_status(job_id)
            
            status = job_status.get("status")
            
            if status == "completed":
                result_data = job_status.get("result_data")
                if result_data is None:
                    raise APIError(f"Job {job_id} completed but no result data found")
                return result_data
            elif status == "failed":
                error_message = job_status.get("error_message", "Job failed")
                raise APIError(f"Job {job_id} failed: {error_message}")
            elif status == "cancelled":
                raise APIError(f"Job {job_id} was cancelled")
            elif status in ["processing", "queued"]:
                # Job still running, wait and poll again
                await asyncio.sleep(poll_interval)
                continue
            else:
                raise APIError(f"Unknown job status: {status}")
    
    async def submit_and_wait(
        self,
        method: str,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Submit a job and automatically wait for completion.
        
        This is a convenience method that combines submit_job() and wait_for_job().
        
        Args:
            method: HTTP method
            path: API endpoint path
            json: Request payload
            poll_interval: Seconds between polls
            max_poll_time: Maximum polling time in seconds
            **kwargs: Additional request arguments
            
        Returns:
            Job result data
        """
        
        job_id = await self.submit_job(method, path, json=json, **kwargs)
        return await self.wait_for_job(job_id, poll_interval, max_poll_time)
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"ZapSEA(base_url='{self.base_url}', auto_poll={self.auto_poll})"
