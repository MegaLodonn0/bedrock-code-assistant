"""Comprehensive test suite for security and core features."""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.security.config import SecurityConfig, AWSCredentialChain
from src.core.security.rate_limiter import RateLimiter, RateLimitConfig, RetryPolicy
from src.core.storage.thread_safety import ThreadSafeStorage, FileLocker, AtomicCounter
from src.core.storage.vector_memory_db import VectorMemoryDB


class TestSecurityConfig:
    """Test security configuration."""
    
    def test_config_from_env(self):
        """Test configuration loading from environment."""
        config = SecurityConfig.from_env()
        assert config.aws_region is not None
        assert config.enable_docker is not None
        assert config.rate_limit_rpm > 0
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = SecurityConfig()
        assert config.validate()
    
    def test_config_invalid_rate_limits(self):
        """Test invalid rate limits are corrected."""
        config = SecurityConfig(rate_limit_rpm=-1, rate_limit_tpm=-1)
        config.validate()
        assert config.rate_limit_rpm > 0
        assert config.rate_limit_tpm > 0


class TestRateLimiter:
    """Test rate limiter."""
    
    @pytest.mark.asyncio
    async def test_rate_limiter_basic(self):
        """Test basic rate limiting."""
        config = RateLimitConfig(requests_per_minute=3, tokens_per_minute=100)
        limiter = RateLimiter(config)
        
        # Should allow 3 requests
        assert await limiter.acquire()
        assert await limiter.acquire()
        assert await limiter.acquire()
        
        # 4th request should fail
        assert not await limiter.acquire()
    
    @pytest.mark.asyncio
    async def test_rate_limiter_stats(self):
        """Test rate limiter statistics."""
        config = RateLimitConfig(requests_per_minute=5, tokens_per_minute=100)
        limiter = RateLimiter(config)
        
        await limiter.acquire(tokens=10)
        await limiter.acquire(tokens=20)
        
        stats = limiter.get_stats()
        assert stats["requests_per_minute"] == 2
        assert stats["tokens_per_minute"] == 30
    
    @pytest.mark.asyncio
    async def test_retry_policy(self):
        """Test retry policy with exponential backoff."""
        policy = RetryPolicy(max_retries=2, base_wait_ms=10)
        
        call_count = 0
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Test error")
            return "success"
        
        result = await policy.execute(failing_func)
        assert result == "success"
        assert call_count == 3


class TestThreadSafety:
    """Test thread-safe operations."""
    
    def test_thread_safe_storage(self):
        """Test thread-safe storage."""
        storage = ThreadSafeStorage()
        
        storage.set("key1", "value1")
        assert storage.get("key1") == "value1"
        
        storage.set("key2", "value2")
        all_data = storage.get_all()
        assert len(all_data) == 2
        
        storage.delete("key1")
        assert storage.get("key1") is None
    
    def test_atomic_counter(self):
        """Test atomic counter."""
        counter = AtomicCounter(initial=10)
        
        assert counter.get() == 10
        assert counter.increment() == 11
        assert counter.increment(5) == 16
        assert counter.decrement() == 15
        assert counter.decrement(5) == 10
    
    def test_file_locker(self):
        """Test file locker."""
        with tempfile.TemporaryDirectory() as tmpdir:
            locker = FileLocker(Path(tmpdir))
            test_file = Path(tmpdir) / "test.txt"
            
            # Write
            locker.write_atomic(str(test_file), "test content")
            
            # Read
            content = locker.read_atomic(str(test_file))
            assert content == "test content"
            
            # Append
            locker.append_atomic(str(test_file), "\nmore content")
            content = locker.read_atomic(str(test_file))
            assert "more content" in content


class TestVectorDB:
    """Test vector database."""
    
    def test_vector_db_init(self):
        """Test vector DB initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = VectorMemoryDB(tmpdir)
            assert db.db_path == Path(tmpdir)
    
    def test_vector_db_add_and_query(self):
        """Test adding and querying documents."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = VectorMemoryDB(tmpdir)
            
            # Add documents
            db.add_memory(
                collection="test",
                documents=["doc1", "doc2", "doc3"],
                metadatas=[{"type": "a"}, {"type": "b"}, {"type": "c"}],
                ids=["id1", "id2", "id3"]
            )
            
            # Get all
            all_data = db.get_all_memory("test")
            assert len(all_data.get("ids", [])) == 3
    
    def test_vector_db_stats(self):
        """Test vector DB statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = VectorMemoryDB(tmpdir)
            
            db.add_memory(
                collection="stats_test",
                documents=["doc1", "doc2"],
                metadatas=[{}, {}],
                ids=["id1", "id2"]
            )
            
            stats = db.get_stats()
            assert "backend" in stats
            assert "collections" in stats


class TestIntegration:
    """Integration tests."""
    
    @pytest.mark.asyncio
    async def test_security_stack(self):
        """Test complete security stack."""
        config = SecurityConfig.from_env()
        config.validate()
        
        limiter = RateLimiter(RateLimitConfig())
        
        # Simulate requests
        for _ in range(5):
            await limiter.acquire()
        
        stats = limiter.get_stats()
        assert stats["requests_per_minute"] == 5
    
    def test_storage_and_memory(self):
        """Test storage and memory integration."""
        storage = ThreadSafeStorage()
        with tempfile.TemporaryDirectory() as tmpdir:
            locker = FileLocker(Path(tmpdir))
            db = VectorMemoryDB(tmpdir)
            
            # Store in memory
            storage.set("session_1", {"user": "test"})
            
            # Store in files
            locker.write_atomic(f"{tmpdir}/session_1.json", '{"user": "test"}')
            
            # Store in vector DB
            db.add_memory(
                collection="sessions",
                documents=["session 1 data"],
                metadatas=[{"session": "1"}],
                ids=["session_1"]
            )
            
            assert storage.get("session_1") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
