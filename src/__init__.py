"""
Event Discovery & Tracking Tool
Main package initialization
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.models.event import Event
from src.utils.config import Config
from src.utils.logger import setup_logger

__all__ = ['Event', 'Config', 'setup_logger']
