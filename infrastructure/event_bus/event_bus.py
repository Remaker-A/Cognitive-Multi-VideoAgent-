"""
Event Bus implementation using Redis Streams.

This module provides the core event bus functionality including:
- Event publishing
- Event subscription
- Event persistence
- Event replay
- Causation tracking
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
import redis.asyncio as redis

from .event import Event, EventType
from .subscriber import EventSubscriber


logger = logging.getLogger(__name__)


class EventBus:
    """
    Event Bus implementation using Redis Streams.
    
    Features:
    - Asynchronous event publishing and consumption
    - Event persistence in Redis Streams
    - Causation ID tracking for event chains
    - Event replay capability
    - Multiple subscribers per event type
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        stream_prefix: str = "event_stream",
        consumer_group: str = "agent_group"
    ):
        """
        Initialize the Event Bus.
        
        Args:
            redis_url: Redis connection URL
            stream_prefix: Prefix for Redis stream keys
            consumer_group: Consumer group name for Redis Streams
        """
        self.redis_url = redis_url
        self.stream_prefix = stream_prefix
        self.consumer_group = consumer_group
        self.redis_client: Optional[redis.Redis] = None
        
        # Subscribers organized by event type
        self.subscribers: Dict[EventType, Set[EventSubscriber]] = {}
        
        # Track all events for causation chain
        self.event_history: List[Event] = []
        
        self._running = False
        self._consumer_tasks: List[asyncio.Task] = []
    
    async def connect(self) -> None:
        """Establish connection to Redis"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info(f"Connected to Redis at {self.redis_url}")
            
            # Create consumer groups for each event type
            await self._create_consumer_groups()
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def _create_consumer_groups(self) -> None:
        """Create consumer groups for all event types"""
        if not self.redis_client:
            return
        
        for event_type in EventType:
            stream_key = self._get_stream_key(event_type)
            try:
                await self.redis_client.xgroup_create(
                    stream_key,
                    self.consumer_group,
                    id="0",
                    mkstream=True
                )
                logger.debug(f"Created consumer group for {event_type.value}")
            except redis.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    logger.warning(f"Error creating consumer group for {event_type.value}: {e}")
    
    def _get_stream_key(self, event_type: EventType) -> str:
        """Get Redis stream key for an event type"""
        return f"{self.stream_prefix}:{event_type.value}"
    
    def subscribe(self, subscriber: EventSubscriber, event_types: List[EventType]) -> None:
        """
        Subscribe an agent to specific event types.
        
        Args:
            subscriber: The subscriber (Agent) to register
            event_types: List of event types to subscribe to
        """
        subscriber.subscribe_to(event_types)
        
        for event_type in event_types:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = set()
            self.subscribers[event_type].add(subscriber)
        
        logger.info(f"{subscriber.name} subscribed to {[et.value for et in event_types]}")
    
    def unsubscribe(self, subscriber: EventSubscriber, event_types: Optional[List[EventType]] = None) -> None:
        """
        Unsubscribe an agent from event types.
        
        Args:
            subscriber: The subscriber to unregister
            event_types: List of event types to unsubscribe from (None = all)
        """
        if event_types is None:
            event_types = list(self.subscribers.keys())
        
        for event_type in event_types:
            if event_type in self.subscribers:
                self.subscribers[event_type].discard(subscriber)
        
        logger.info(f"{subscriber.name} unsubscribed from {[et.value for et in event_types]}")
    
    async def publish(self, event: Event) -> str:
        """
        Publish an event to the bus.
        
        Args:
            event: The event to publish
            
        Returns:
            The event ID
        """
        if not self.redis_client:
            raise RuntimeError("Event Bus not connected to Redis")
        
        # Add to history for causation tracking
        self.event_history.append(event)
        
        # Serialize event
        event_data = json.dumps(event.to_dict())
        
        # Publish to Redis Stream
        stream_key = self._get_stream_key(event.type)
        message_id = await self.redis_client.xadd(
            stream_key,
            {"data": event_data}
        )
        
        logger.info(
            f"Published event {event.event_id} ({event.type.value}) "
            f"from {event.actor} to stream {stream_key}"
        )
        
        # Notify local subscribers immediately (for same-process agents)
        await self._notify_local_subscribers(event)
        
        return event.event_id
    
    async def _notify_local_subscribers(self, event: Event) -> None:
        """Notify subscribers in the same process"""
        if event.type in self.subscribers:
            tasks = []
            for subscriber in self.subscribers[event.type]:
                tasks.append(subscriber.handle_event(event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def start_consuming(self) -> None:
        """Start consuming events from Redis Streams"""
        if not self.redis_client:
            raise RuntimeError("Event Bus not connected to Redis")
        
        self._running = True
        
        # Start a consumer task for each subscribed event type
        for event_type in self.subscribers.keys():
            task = asyncio.create_task(self._consume_stream(event_type))
            self._consumer_tasks.append(task)
        
        logger.info(f"Started consuming {len(self._consumer_tasks)} event streams")
    
    async def stop_consuming(self) -> None:
        """Stop consuming events"""
        self._running = False
        
        # Cancel all consumer tasks
        for task in self._consumer_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._consumer_tasks, return_exceptions=True)
        
        self._consumer_tasks.clear()
        logger.info("Stopped consuming event streams")
    
    async def _consume_stream(self, event_type: EventType) -> None:
        """
        Consume events from a specific stream.
        
        Args:
            event_type: The event type to consume
        """
        stream_key = self._get_stream_key(event_type)
        consumer_name = f"consumer_{asyncio.current_task().get_name()}"
        
        logger.info(f"Started consuming stream {stream_key}")
        
        while self._running:
            try:
                # Read from stream
                messages = await self.redis_client.xreadgroup(
                    self.consumer_group,
                    consumer_name,
                    {stream_key: ">"},
                    count=10,
                    block=1000  # Block for 1 second
                )
                
                for stream, message_list in messages:
                    for message_id, message_data in message_list:
                        try:
                            # Deserialize event
                            event_dict = json.loads(message_data["data"])
                            event = Event.from_dict(event_dict)
                            
                            # Notify subscribers
                            if event.type in self.subscribers:
                                tasks = []
                                for subscriber in self.subscribers[event.type]:
                                    tasks.append(subscriber.handle_event(event))
                                
                                await asyncio.gather(*tasks, return_exceptions=True)
                            
                            # Acknowledge message
                            await self.redis_client.xack(stream_key, self.consumer_group, message_id)
                            
                        except Exception as e:
                            logger.error(f"Error processing message {message_id}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error consuming stream {stream_key}: {e}")
                await asyncio.sleep(1)
    
    async def replay_events(
        self,
        project_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None
    ) -> List[Event]:
        """
        Replay events for debugging or recovery.
        
        Args:
            project_id: Project ID to filter events
            start_time: Start time for replay (None = from beginning)
            end_time: End time for replay (None = to end)
            event_types: Filter by event types (None = all types)
            
        Returns:
            List of events matching the criteria
        """
        if not self.redis_client:
            raise RuntimeError("Event Bus not connected to Redis")
        
        events = []
        
        # Determine which streams to read
        streams_to_read = event_types if event_types else list(EventType)
        
        for event_type in streams_to_read:
            stream_key = self._get_stream_key(event_type)
            
            # Read all messages from stream
            messages = await self.redis_client.xrange(stream_key)
            
            for message_id, message_data in messages:
                try:
                    event_dict = json.loads(message_data["data"])
                    event = Event.from_dict(event_dict)
                    
                    # Filter by project_id
                    if event.project_id != project_id:
                        continue
                    
                    # Filter by time range
                    event_time = datetime.fromisoformat(event.timestamp)
                    if start_time and event_time < start_time:
                        continue
                    if end_time and event_time > end_time:
                        continue
                    
                    events.append(event)
                    
                except Exception as e:
                    logger.error(f"Error deserializing event: {e}")
        
        # Sort by timestamp
        events.sort(key=lambda e: e.timestamp)
        
        return events
    
    def get_causation_chain(self, event_id: str) -> List[Event]:
        """
        Get the causation chain for an event.
        
        Args:
            event_id: The event ID to trace
            
        Returns:
            List of events in the causation chain (oldest to newest)
        """
        chain = []
        current_id = event_id
        
        # Build a map of event_id to event
        event_map = {e.event_id: e for e in self.event_history}
        
        # Trace back through causation_id
        while current_id and current_id in event_map:
            event = event_map[current_id]
            chain.insert(0, event)
            current_id = event.causation_id
        
        return chain
    
    async def get_project_events(self, project_id: str) -> List[Event]:
        """
        Get all events for a specific project.
        
        Args:
            project_id: The project ID
            
        Returns:
            List of events for the project
        """
        return await self.replay_events(project_id)
