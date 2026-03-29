"""Thread-safe operations for multi-agent concurrency."""

import threading
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from contextlib import contextmanager
from filelock import FileLock

logger = logging.getLogger(__name__)


class ThreadSafeStorage:
    """Thread-safe dictionary with RLock."""
    
    def __init__(self):
        """Initialize thread-safe storage."""
        self._data: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value with lock."""
        with self._lock:
            return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value with lock."""
        with self._lock:
            self._data[key] = value
    
    def delete(self, key: str) -> None:
        """Delete value with lock."""
        with self._lock:
            self._data.pop(key, None)
    
    def clear(self) -> None:
        """Clear all data."""
        with self._lock:
            self._data.clear()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all data (copy)."""
        with self._lock:
            return self._data.copy()
    
    def update(self, data: Dict[str, Any]) -> None:
        """Update multiple values."""
        with self._lock:
            self._data.update(data)


class FileLocker:
    """Thread-safe file operations with FileLock."""
    
    def __init__(self, lock_dir: Optional[Path] = None):
        """Initialize file locker."""
        self.lock_dir = lock_dir or Path("./locks")
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, FileLock] = {}
    
    def _get_lock(self, file_path: str) -> FileLock:
        """Get or create lock for file."""
        if file_path not in self._locks:
            lock_file = self.lock_dir / f"{Path(file_path).stem}.lock"
            self._locks[file_path] = FileLock(str(lock_file), timeout=30)
        return self._locks[file_path]
    
    @contextmanager
    def lock_file(self, file_path: str):
        """Context manager for file locking."""
        lock = self._get_lock(file_path)
        try:
            with lock:
                logger.debug(f"🔒 Locked {file_path}")
                yield
        finally:
            logger.debug(f"🔓 Unlocked {file_path}")
    
    def read_atomic(self, file_path: str) -> str:
        """Read file atomically."""
        with self.lock_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def write_atomic(self, file_path: str, content: str) -> None:
        """Write file atomically."""
        with self.lock_file(file_path):
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    def append_atomic(self, file_path: str, content: str) -> None:
        """Append to file atomically."""
        with self.lock_file(file_path):
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)


class AtomicCounter:
    """Thread-safe counter."""
    
    def __init__(self, initial: int = 0):
        """Initialize counter."""
        self._value = initial
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment counter."""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement counter."""
        with self._lock:
            self._value -= amount
            return self._value
    
    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value
    
    def set(self, value: int) -> None:
        """Set value."""
        with self._lock:
            self._value = value


class RWLock:
    """Reader-writer lock (multiple readers, single writer)."""
    
    def __init__(self):
        """Initialize RWLock."""
        self._readers = 0
        self._writers = 0
        self._read_ready = threading.Condition(threading.RLock())
        self._write_ready = threading.Condition(threading.RLock())
    
    @contextmanager
    def read_lock(self):
        """Acquire read lock."""
        self._read_ready.acquire()
        try:
            self._readers += 1
            if self._readers == 1:
                self._write_ready.acquire()
            self._read_ready.release()
            
            logger.debug("📖 Read lock acquired")
            yield
        finally:
            self._read_ready.acquire()
            try:
                self._readers -= 1
                if self._readers == 0:
                    self._write_ready.release()
            finally:
                self._read_ready.release()
            logger.debug("📖 Read lock released")
    
    @contextmanager
    def write_lock(self):
        """Acquire write lock."""
        self._write_ready.acquire()
        self._readers = float('inf')  # Prevent new readers
        logger.debug("✍️  Write lock acquired")
        
        try:
            yield
        finally:
            self._readers = 0
            self._write_ready.release()
            logger.debug("✍️  Write lock released")


# Global instances
_thread_safe_storage = ThreadSafeStorage()
_file_locker = FileLocker()


def get_thread_safe_storage() -> ThreadSafeStorage:
    """Get global thread-safe storage."""
    return _thread_safe_storage


def get_file_locker() -> FileLocker:
    """Get global file locker."""
    return _file_locker
