"""
Pydantic models for Victoria Dates API responses
"""

from typing import List, Optional
from pydantic import BaseModel


class ImportantDate(BaseModel):
    """Model for a single important date"""
    uuid: str
    name: str
    description: Optional[str] = None
    date: str
    type: str


class ImportantDatesResponse(BaseModel):
    """Model for the API response containing multiple dates"""
    dates: List[ImportantDate] 