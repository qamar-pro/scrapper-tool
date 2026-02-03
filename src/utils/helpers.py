"""
Helper Utilities
Common helper functions used across the application
"""

import time
import hashlib
from typing import Any, Callable, Optional
from functools import wraps
from datetime import datetime, timedelta
import requests
from fake_useragent import UserAgent


def generate_id(text: str) -> str:
    """Generate unique ID from text"""
    return hashlib.md5(text.encode()).hexdigest()[:12]


def retry_on_failure(max_retries: int = 3, delay: float = 2.0):
    """
    Decorator for retrying function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))
                    continue
            
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def get_random_user_agent() -> str:
    """Get a random user agent string"""
    try:
        ua = UserAgent()
        return ua.random
    except Exception:
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'


def make_request(url: str, timeout: int = 30, headers: Optional[dict] = None) -> requests.Response:
    """
    Make HTTP request with error handling
    
    Args:
        url: URL to request
        timeout: Request timeout in seconds
        headers: Optional headers
    
    Returns:
        Response object
    """
    if headers is None:
        headers = {'User-Agent': get_random_user_agent()}
    
    response = requests.get(url, timeout=timeout, headers=headers)
    response.raise_for_status()
    return response


def parse_date(date_string: str) -> Optional[datetime]:
    """
    Parse date string to datetime object
    Handles multiple date formats
    """
    from dateutil import parser
    try:
        return parser.parse(date_string)
    except Exception:
        return None


def is_date_expired(date_string: str, days_offset: int = 0) -> bool:
    """
    Check if date has expired
    
    Args:
        date_string: Date string to check
        days_offset: Days offset from today (0 = today)
    
    Returns:
        True if expired, False otherwise
    """
    date_obj = parse_date(date_string)
    if not date_obj:
        return False
    
    threshold_date = datetime.now() + timedelta(days=days_offset)
    return date_obj < threshold_date


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def truncate_string(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate string to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
