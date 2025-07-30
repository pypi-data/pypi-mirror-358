"""
Utility functions for the smartpylogger package

Unsure of what this will actually contain
"""

import json
import hashlib
import time
from typing import Dict, Any, Optional


def format_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """Formatting and structure schema data for API submission"""
    return {
        "schema_version": "1.0",
        "timestamp": time.time(),
        "data": data,
    }

def format_timestamp(timestamp: float) -> str:
    """Format timestamp for logging"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))

def create_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{int(time.time() * 1000)}_{hash(time.time()) % 10000}"

