import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

class RetryError(Exception):
    """Custom exception raised when all retry attempts fail."""
    pass

def retry(max_retries: int = 1, delay: int = 300, retry_on_exceptions: tuple = (Exception,)):
    """
    A decorator to retry a function if it raises one of the specified exceptions.
    
    Args:
        max_retries (int): Number of retry attempts
        delay (int): Delay in seconds between retries
        retry_on_exceptions (tuple): Tuple of exception types to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            last_exception = None

            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except retry_on_exceptions as e:
                    last_exception = e
                    if retries < max_retries:
                        logger.warning(
                            f"{func.__name__} failed with {type(e).__name__}: {e}. Retrying in {delay // 60} minutes..."
                        )
                        time.sleep(delay)
                        retries += 1
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {type(e).__name__}: {e}")
                        raise RetryError(f"Function {func.__name__} failed after {max_retries + 1} attempts.") from e
            return None  # Shouldn't reach here
        return wrapper
    return decorator