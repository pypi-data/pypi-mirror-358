"""
ZapSEA Python SDK - Jobs Resource

Provides interface for managing async jobs and polling for completion.
"""

from typing import List, Dict, Any, Optional
import logging

from ..types import JobInfo, JobStatus
from ..exceptions import ResourceNotFoundError, APIError

logger = logging.getLogger(__name__)


class Jobs:
    """
    Jobs resource for managing async operations.
    
    Provides methods for:
    - Getting job status
    - Cancelling jobs
    - Listing user jobs
    - Waiting for completion
    """
    
    def __init__(self, client):
        """Initialize Jobs resource with client reference."""
        self._client = client
    
    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the current status of a job.
        
        Args:
            job_id: Job ID to check
            
        Returns:
            Job status information
            
        Raises:
            ResourceNotFoundError: Job not found
            APIError: API request failed
            
        Example:
            ```python
            status = await client.jobs.get_status("job_123")
            print(f"Status: {status['status']}")
            print(f"Progress: {status['progress_percentage']}%")
            ```
        """
        
        try:
            response = await self._client.request(
                method="GET",
                path=f"/v2/jobs/{job_id}"
            )
            
            return response
            
        except APIError as e:
            if e.status_code == 404:
                raise ResourceNotFoundError(f"Job {job_id} not found", "job", job_id)
            raise
    
    async def cancel(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a running job.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            Cancellation confirmation
            
        Raises:
            ResourceNotFoundError: Job not found
            APIError: Job cannot be cancelled or API error
            
        Example:
            ```python
            result = await client.jobs.cancel("job_123")
            print(f"Cancelled: {result['cancelled']}")
            ```
        """
        
        try:
            response = await self._client.request(
                method="DELETE",
                path=f"/v2/jobs/{job_id}"
            )
            
            logger.info(f"Job {job_id} cancelled")
            return response
            
        except APIError as e:
            if e.status_code == 404:
                raise ResourceNotFoundError(f"Job {job_id} not found", "job", job_id)
            elif e.status_code == 409:
                raise APIError(f"Job {job_id} cannot be cancelled (already completed or failed)")
            raise
    
    async def list(
        self,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List jobs for the current user.
        
        Args:
            status_filter: Filter by job status (processing, completed, failed, cancelled)
            limit: Maximum number of jobs to return (max: 100)
            offset: Number of jobs to skip for pagination
            
        Returns:
            List of jobs with pagination info
            
        Example:
            ```python
            jobs = await client.jobs.list(status_filter="completed", limit=20)
            
            for job in jobs['jobs']:
                print(f"Job {job['job_id']}: {job['status']}")
            
            print(f"Total: {jobs['total_count']}")
            ```
        """
        
        if limit > 100:
            limit = 100
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if status_filter:
            params["status_filter"] = status_filter
        
        response = await self._client.request(
            method="GET",
            path="/v2/jobs/",
            params=params
        )
        
        return response
    
    async def wait_for_completion(
        self,
        job_id: str,
        poll_interval: Optional[int] = None,
        max_poll_time: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Wait for a job to complete and return the result.
        
        Args:
            job_id: Job ID to wait for
            poll_interval: Seconds between polls (uses client default if None)
            max_poll_time: Maximum time to wait (uses client default if None)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Job result data
            
        Raises:
            JobTimeoutError: Job didn't complete in time
            APIError: Job failed or API error
            
        Example:
            ```python
            def on_progress(job_status):
                print(f"Progress: {job_status['progress_percentage']}%")
            
            result = await client.jobs.wait_for_completion(
                "job_123",
                progress_callback=on_progress
            )
            ```
        """
        
        return await self._client.wait_for_job(
            job_id=job_id,
            poll_interval=poll_interval,
            max_poll_time=max_poll_time
        )
    
    async def get_result(self, job_id: str) -> Dict[str, Any]:
        """
        Get the result of a completed job.
        
        Args:
            job_id: Job ID to get result for
            
        Returns:
            Job result data
            
        Raises:
            ResourceNotFoundError: Job not found
            APIError: Job not completed or failed
            
        Example:
            ```python
            result = await client.jobs.get_result("job_123")
            print(f"Simulation ID: {result['simulation_id']}")
            ```
        """
        
        job_status = await self.get_status(job_id)
        
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
        else:
            raise APIError(f"Job {job_id} is not completed (status: {status})")
    
    async def retry_failed_job(self, job_id: str) -> str:
        """
        Retry a failed job with the same parameters.
        
        Args:
            job_id: Failed job ID to retry
            
        Returns:
            New job ID for the retry
            
        Raises:
            ResourceNotFoundError: Job not found
            APIError: Job is not in failed state or cannot be retried
        """
        
        try:
            response = await self._client.request(
                method="POST",
                path=f"/v2/jobs/{job_id}/retry"
            )
            
            new_job_id = response.get("job_id")
            if not new_job_id:
                raise APIError("Invalid retry response: missing job_id")
            
            logger.info(f"Retrying job {job_id} as {new_job_id}")
            return new_job_id
            
        except APIError as e:
            if e.status_code == 404:
                raise ResourceNotFoundError(f"Job {job_id} not found", "job", job_id)
            elif e.status_code == 409:
                raise APIError(f"Job {job_id} cannot be retried (not in failed state)")
            raise
