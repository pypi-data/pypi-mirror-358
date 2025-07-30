# backend/smartpylogger/__init__.py

# Version (optional, but good practice)
__version__ = "0.1.0"

# Import and expose your main classes/functions
from .logger import LoggingMiddleware
from .utils import *  # if you want to expose all utils

# Define what is available for import *
__all__ = ["LoggingMiddleware"]
