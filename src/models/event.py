"""
Event Model
Represents an event with all required fields
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import hashlib


@dataclass
class Event:
    """Event data model"""
    
    event_name: str
    date: str
    venue: str
    city: str
    category: str
    url: str
    source: str  # bookmyshow or district
    status: str = "Active"
    last_updated: datetime = field(default_factory=datetime.now)
    event_id: Optional[str] = None
    
    def __post_init__(self):
        """Generate unique event ID after initialization"""
        if not self.event_id:
            self.event_id = self.generate_event_id()
    
    def generate_event_id(self) -> str:
        """Generate unique ID based on event details"""
        unique_string = f"{self.event_name}_{self.date}_{self.venue}_{self.city}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def to_dict(self) -> dict:
        """Convert event to dictionary"""
        return {
            'Event ID': self.event_id,
            'Event Name': self.event_name,
            'Date': self.date,
            'Venue': self.venue,
            'City': self.city,
            'Category': self.category,
            'URL': self.url,
            'Source': self.source,
            'Status': self.status,
            'Last Updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def is_expired(self, reference_date: Optional[datetime] = None) -> bool:
        """Check if event has expired"""
        if reference_date is None:
            reference_date = datetime.now()
        
        try:
            from dateutil import parser
            event_date = parser.parse(self.date)
            return event_date < reference_date
        except Exception:
            return False
    
    def __str__(self) -> str:
        """String representation"""
        return f"Event({self.event_name} - {self.city} - {self.date})"
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return (f"Event(id={self.event_id}, name={self.event_name}, "
                f"city={self.city}, date={self.date}, status={self.status})")
