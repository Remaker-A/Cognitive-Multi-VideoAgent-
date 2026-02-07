"""
Event subscriber interface and base class.
"""

from abc import ABC, abstractmethod
from typing import Callable, List
from .event import Event, EventType


class EventSubscriber(ABC):
    """
    Base class for event subscribers.
    
    Agents should inherit from this class and implement the handle_event method.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.subscribed_events: List[EventType] = []
    
    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        """
        Handle an incoming event.
        
        Args:
            event: The event to handle
        """
        pass
    
    def subscribe_to(self, event_types: List[EventType]) -> None:
        """
        Subscribe to specific event types.
        
        Args:
            event_types: List of event types to subscribe to
        """
        self.subscribed_events = event_types
    
    def is_subscribed_to(self, event_type: EventType) -> bool:
        """
        Check if this subscriber is subscribed to a specific event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            True if subscribed, False otherwise
        """
        return event_type in self.subscribed_events


class CallbackSubscriber(EventSubscriber):
    """
    A simple subscriber that uses a callback function.
    
    Useful for testing and simple event handlers.
    """
    
    def __init__(self, name: str, callback: Callable[[Event], None]):
        super().__init__(name)
        self.callback = callback
    
    async def handle_event(self, event: Event) -> None:
        """Handle event by calling the callback function"""
        if callable(self.callback):
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(event)
            else:
                self.callback(event)


import asyncio
