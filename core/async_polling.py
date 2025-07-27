"""
Async Response Polling Strategy for API Client.

This module provides utilities for handling asynchronous operations that require
polling for completion status. It implements a configurable polling mechanism
with exponential backoff and timeout handling.
"""
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class PollingStatus(Enum):
    """Status of a polling operation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AsyncPollingStrategy:
    """
    Handles async polling for long-running operations.
    
    This strategy is designed to work with API endpoints that return a task ID
    and require polling to check completion status.
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_factor: float = 1.5,
        max_attempts: int = 60,
        timeout_seconds: float = 300.0
    ):
        """
        Initialize polling strategy.
        
        Args:
            initial_delay: Initial delay between polls in seconds
            max_delay: Maximum delay between polls in seconds
            backoff_factor: Factor to increase delay after each poll
            max_attempts: Maximum number of polling attempts
            timeout_seconds: Total timeout for the operation
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.max_attempts = max_attempts
        self.timeout_seconds = timeout_seconds
    
    async def poll_until_complete(
        self,
        status_checker: Callable[[], Awaitable[Dict[str, Any]]],
        completion_checker: Callable[[Dict[str, Any]], bool],
        error_checker: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> Dict[str, Any]:
        """
        Poll until operation completes or times out.
        
        Args:
            status_checker: Async function that returns current status
            completion_checker: Function that checks if operation is complete
            error_checker: Optional function that checks if operation failed
            
        Returns:
            Dict containing the final status and result
            
        Raises:
            TimeoutError: If operation times out
            RuntimeError: If operation fails
        """
        start_time = datetime.utcnow()
        delay = self.initial_delay
        attempts = 0
        
        logger.info(f"Starting async polling with {self.max_attempts} max attempts")
        
        while attempts < self.max_attempts:
            # Check timeout
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            if elapsed > self.timeout_seconds:
                logger.error(f"Polling timeout after {elapsed:.2f} seconds")
                raise TimeoutError(f"Operation timed out after {elapsed:.2f} seconds")
            
            try:
                # Get current status
                status_result = await status_checker()
                attempts += 1
                
                logger.debug(f"Poll attempt {attempts}: {status_result}")
                
                # Check if operation failed
                if error_checker and error_checker(status_result):
                    error_msg = status_result.get('error', 'Operation failed')
                    logger.error(f"Operation failed: {error_msg}")
                    raise RuntimeError(f"Operation failed: {error_msg}")
                
                # Check if operation completed
                if completion_checker(status_result):
                    logger.info(f"Operation completed after {attempts} attempts")
                    return {
                        "status": PollingStatus.COMPLETED.value,
                        "result": status_result,
                        "attempts": attempts,
                        "elapsed_seconds": elapsed
                    }
                
                # Wait before next poll
                if attempts < self.max_attempts:
                    logger.debug(f"Waiting {delay:.2f}s before next poll")
                    await asyncio.sleep(delay)
                    
                    # Increase delay with backoff
                    delay = min(delay * self.backoff_factor, self.max_delay)
                
            except Exception as e:
                logger.error(f"Error during polling attempt {attempts}: {e}")
                if attempts >= self.max_attempts:
                    raise
                
                # Wait before retry on error
                await asyncio.sleep(delay)
                delay = min(delay * self.backoff_factor, self.max_delay)
        
        # Max attempts reached
        logger.error(f"Max polling attempts ({self.max_attempts}) reached")
        raise TimeoutError(f"Operation did not complete within {self.max_attempts} attempts")


class APIClientPollingMixin:
    """
    Mixin to add async polling capabilities to API client.
    
    This mixin provides methods for handling long-running operations
    that require polling for completion.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.polling_strategy = AsyncPollingStrategy()
    
    async def _poll_operation_status(
        self,
        discord_user,
        operation_id: str,
        status_endpoint: str
    ) -> Dict[str, Any]:
        """
        Poll for operation status.
        
        Args:
            discord_user: Discord user for authentication
            operation_id: ID of the operation to check
            status_endpoint: API endpoint to check status
            
        Returns:
            Dict containing operation status
        """
        endpoint = f"{status_endpoint}/{operation_id}"
        return await self._make_request("GET", endpoint, discord_user)
    
    async def _wait_for_operation_completion(
        self,
        discord_user,
        operation_id: str,
        status_endpoint: str,
        completion_statuses: list = None,
        error_statuses: list = None
    ) -> Dict[str, Any]:
        """
        Wait for an async operation to complete using polling.
        
        Args:
            discord_user: Discord user for authentication
            operation_id: ID of the operation to wait for
            status_endpoint: API endpoint to check status
            completion_statuses: List of statuses that indicate completion
            error_statuses: List of statuses that indicate failure
            
        Returns:
            Dict containing the final operation result
        """
        if completion_statuses is None:
            completion_statuses = ["completed", "success", "finished"]
        
        if error_statuses is None:
            error_statuses = ["failed", "error", "cancelled"]
        
        async def status_checker():
            return await self._poll_operation_status(
                discord_user, operation_id, status_endpoint
            )
        
        def completion_checker(status_result: Dict[str, Any]) -> bool:
            status = status_result.get("status", "").lower()
            return status in completion_statuses
        
        def error_checker(status_result: Dict[str, Any]) -> bool:
            status = status_result.get("status", "").lower()
            return status in error_statuses
        
        return await self.polling_strategy.poll_until_complete(
            status_checker, completion_checker, error_checker
        )
    
    async def _submit_async_operation(
        self,
        discord_user,
        endpoint: str,
        data: Dict[str, Any],
        wait_for_completion: bool = True,
        status_endpoint: str = None
    ) -> Dict[str, Any]:
        """
        Submit an async operation and optionally wait for completion.
        
        Args:
            discord_user: Discord user for authentication
            endpoint: API endpoint to submit operation
            data: Operation data
            wait_for_completion: Whether to wait for completion
            status_endpoint: Endpoint to check operation status
            
        Returns:
            Dict containing operation result or status
        """
        # Submit the operation
        result = await self._make_request("POST", endpoint, discord_user, json=data)
        
        # If not waiting for completion, return immediately
        if not wait_for_completion:
            return result
        
        # Extract operation ID from result
        operation_id = result.get("operation_id") or result.get("task_id") or result.get("id")
        
        if not operation_id:
            logger.warning("No operation ID returned, cannot poll for completion")
            return result
        
        # Use provided status endpoint or derive from submission endpoint
        if not status_endpoint:
            status_endpoint = f"{endpoint}/status"
        
        # Wait for completion
        return await self._wait_for_operation_completion(
            discord_user, operation_id, status_endpoint
        )