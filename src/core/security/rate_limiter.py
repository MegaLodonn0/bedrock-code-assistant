"""Rate limiting with exponential backoff for API stability."""

import asyncio
import time
import logging
from typing import Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 30
    tokens_per_minute: int = 40000
    max_retries: int = 5
    base_wait_ms: int = 100
    max_wait_ms: int = 30000


class RateLimiter:
    """Rate limiter with exponential backoff."""
    
    def __init__(self, config: RateLimitConfig):
        """Initialize rate limiter."""
        self.config = config
        self.request_times: deque = deque()
        self.token_counts: deque = deque()
        self.lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire rate limit slot."""
        async with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Clean old entries
            while self.request_times and self.request_times[0] < minute_ago:
                self.request_times.popleft()
            
            while self.token_counts and self.token_counts[0][0] < minute_ago:
                self.token_counts.popleft()
            
            # Check RPM limit
            if len(self.request_times) >= self.config.requests_per_minute:
                return False
            
            # Check TPM limit
            total_tokens = sum(count for _, count in self.token_counts)
            if total_tokens + tokens > self.config.tokens_per_minute:
                return False
            
            self.request_times.append(now)
            self.token_counts.append((now, tokens))
            return True
    
    async def wait_and_acquire(self, tokens: int = 1) -> None:
        """Wait until rate limit slot is available."""
        retry_count = 0
        wait_ms = self.config.base_wait_ms
        
        while not await self.acquire(tokens):
            if retry_count >= self.config.max_retries:
                raise RuntimeError("Rate limit exceeded - max retries reached")
            
            await asyncio.sleep(wait_ms / 1000)
            
            # Exponential backoff
            wait_ms = min(int(wait_ms * 1.5), self.config.max_wait_ms)
            retry_count += 1
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        requests = sum(1 for t in self.request_times if t > minute_ago)
        tokens = sum(count for t, count in self.token_counts if t > minute_ago)
        
        return {
            "requests_per_minute": requests,
            "tokens_per_minute": tokens,
            "rpm_limit": self.config.requests_per_minute,
            "tpm_limit": self.config.tokens_per_minute,
            "rpm_remaining": self.config.requests_per_minute - requests,
            "tpm_remaining": self.config.tokens_per_minute - tokens,
        }


class RetryPolicy:
    """Retry with exponential backoff."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_wait_ms: int = 100,
        max_wait_ms: int = 10000,
        backoff_factor: float = 1.5,
        jitter: bool = True
    ):
        """Initialize retry policy."""
        self.max_retries = max_retries
        self.base_wait_ms = base_wait_ms
        self.max_wait_ms = max_wait_ms
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry policy."""
        import random
        
        wait_ms = self.base_wait_ms
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                if attempt > 0:
                    logger.info(f"✅ Succeeded after {attempt} retries")
                return result
            
            except Exception as e:
                last_error = e
                
                if attempt < self.max_retries:
                    # Add jitter to prevent thundering herd
                    if self.jitter:
                        jitter_ms = random.randint(0, wait_ms // 2)
                        actual_wait = (wait_ms + jitter_ms) / 1000
                    else:
                        actual_wait = wait_ms / 1000
                    
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}. Retrying in {actual_wait:.1f}s...")
                    await asyncio.sleep(actual_wait)
                    
                    wait_ms = min(int(wait_ms * self.backoff_factor), self.max_wait_ms)
        
        raise last_error or RuntimeError("All retries exhausted")


def create_rate_limiter(
    rpm: int = 30,
    tpm: int = 40000
) -> RateLimiter:
    """Create rate limiter instance."""
    config = RateLimitConfig(
        requests_per_minute=rpm,
        tokens_per_minute=tpm
    )
    return RateLimiter(config)


def create_retry_policy(
    max_retries: int = 3,
    base_wait_ms: int = 100
) -> RetryPolicy:
    """Create retry policy instance."""
    return RetryPolicy(
        max_retries=max_retries,
        base_wait_ms=base_wait_ms
    )


# Global instances
_rate_limiter: Optional[RateLimiter] = None
_retry_policy: Optional[RetryPolicy] = None


def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = create_rate_limiter()
    return _rate_limiter


def get_retry_policy() -> RetryPolicy:
    """Get or create retry policy."""
    global _retry_policy
    if _retry_policy is None:
        _retry_policy = create_retry_policy()
    return _retry_policy
