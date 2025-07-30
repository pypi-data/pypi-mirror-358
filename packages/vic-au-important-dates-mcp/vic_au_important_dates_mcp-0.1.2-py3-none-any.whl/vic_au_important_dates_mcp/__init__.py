"""
Victoria Important Dates MCP - A Python client for Victoria, Australia important dates API
"""

from .client import VictoriaDatesClient
from .models import ImportantDate, ImportantDatesResponse

__version__ = "0.1.0"
__all__ = ["VictoriaDatesClient", "ImportantDate", "ImportantDatesResponse"] 