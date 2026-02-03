"""
Base Storage
Abstract base class for all storage backends
"""

from abc import ABC, abstractmethod
from typing import List
from src.models.event import Event


class BaseStorage(ABC):
    """Abstract base storage class"""
    
    def __init__(self):
        """Initialize storage"""
        self.events: List[Event] = []
    
    @abstractmethod
    def save_events(self, events: List[Event]) -> bool:
        """
        Save events to storage
        
        Args:
            events: List of Event objects
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def load_events(self) -> List[Event]:
        """
        Load events from storage
        
        Returns:
            List of Event objects
        """
        pass
    
    @abstractmethod
    def update_event(self, event: Event) -> bool:
        """
        Update existing event
        
        Args:
            event: Event object to update
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """
        Delete event by ID
        
        Args:
            event_id: Event ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def mark_expired_events(self) -> int:
        """
        Mark expired events
        
        Returns:
            Number of events marked as expired
        """
        pass
    
    def deduplicate_events(self, new_events: List[Event], existing_events: List[Event]) -> List[Event]:
        """
        Deduplicate events based on event_id
        
        Args:
            new_events: Newly scraped events
            existing_events: Events already in storage
        
        Returns:
            List of truly new events
        """
        existing_ids = {event.event_id for event in existing_events}
        return [event for event in new_events if event.event_id not in existing_ids]
    
    def merge_events(self, new_events: List[Event], existing_events: List[Event]) -> List[Event]:
        """
        Merge new events with existing events
        Updates existing events and adds new ones
        
        Args:
            new_events: Newly scraped events
            existing_events: Events already in storage
        
        Returns:
            Merged list of events
        """
        event_dict = {event.event_id: event for event in existing_events}
        
        # Update existing events and add new ones
        for event in new_events:
            if event.event_id in event_dict:
                # Update existing event
                event_dict[event.event_id].status = "Updated"
                event_dict[event.event_id].last_updated = event.last_updated
            else:
                # Add new event
                event_dict[event.event_id] = event
        
        return list(event_dict.values())
