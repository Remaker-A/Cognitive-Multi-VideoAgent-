"""
Tests for Event Bus infrastructure.
"""

import pytest
import asyncio
from datetime import datetime
from typing import List

from src.infrastructure.event_bus import EventBus, Event, EventType, EventSubscriber


class TestSubscriber(EventSubscriber):
    """Test subscriber for unit tests"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.received_events: List[Event] = []
    
    async def handle_event(self, event: Event) -> None:
        """Store received events"""
        self.received_events.append(event)


@pytest.fixture
async def event_bus():
    """Create and connect an event bus for testing"""
    bus = EventBus(redis_url="redis://localhost:6379")
    await bus.connect()
    yield bus
    await bus.disconnect()


@pytest.mark.asyncio
async def test_event_creation():
    """Test event creation and serialization"""
    event = Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser",
        payload={"title": "Test Project"}
    )
    
    assert event.event_id.startswith("EV-")
    assert event.project_id == "PROJ-001"
    assert event.type == EventType.PROJECT_CREATED
    assert event.actor == "RequirementParser"
    
    # Test serialization
    event_dict = event.to_dict()
    assert event_dict["type"] == "PROJECT_CREATED"
    
    # Test deserialization
    restored_event = Event.from_dict(event_dict)
    assert restored_event.event_id == event.event_id
    assert restored_event.type == event.type


@pytest.mark.asyncio
async def test_subscribe_and_publish(event_bus):
    """Test subscribing to events and publishing"""
    # Create subscriber
    subscriber = TestSubscriber("TestAgent")
    
    # Subscribe to PROJECT_CREATED events
    event_bus.subscribe(subscriber, [EventType.PROJECT_CREATED])
    
    # Publish event
    event = Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser",
        payload={"title": "Test Project"}
    )
    
    event_id = await event_bus.publish(event)
    
    # Wait a bit for event processing
    await asyncio.sleep(0.1)
    
    # Verify subscriber received the event
    assert len(subscriber.received_events) == 1
    assert subscriber.received_events[0].event_id == event_id


@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus):
    """Test multiple subscribers receiving the same event"""
    # Create multiple subscribers
    subscriber1 = TestSubscriber("Agent1")
    subscriber2 = TestSubscriber("Agent2")
    
    # Both subscribe to the same event type
    event_bus.subscribe(subscriber1, [EventType.IMAGE_GENERATED])
    event_bus.subscribe(subscriber2, [EventType.IMAGE_GENERATED])
    
    # Publish event
    event = Event(
        project_id="PROJ-001",
        type=EventType.IMAGE_GENERATED,
        actor="ImageGenAgent",
        payload={"artifact_url": "s3://test/image.png"}
    )
    
    await event_bus.publish(event)
    await asyncio.sleep(0.1)
    
    # Both subscribers should receive the event
    assert len(subscriber1.received_events) == 1
    assert len(subscriber2.received_events) == 1


@pytest.mark.asyncio
async def test_causation_tracking(event_bus):
    """Test causation ID tracking"""
    # Publish first event
    event1 = Event(
        project_id="PROJ-001",
        type=EventType.SCENE_WRITTEN,
        actor="ScriptWriter"
    )
    event1_id = await event_bus.publish(event1)
    
    # Publish second event caused by first
    event2 = Event(
        project_id="PROJ-001",
        type=EventType.SHOT_PLANNED,
        actor="ShotDirector",
        causation_id=event1_id
    )
    event2_id = await event_bus.publish(event2)
    
    # Publish third event caused by second
    event3 = Event(
        project_id="PROJ-001",
        type=EventType.IMAGE_GENERATED,
        actor="ImageGenAgent",
        causation_id=event2_id
    )
    event3_id = await event_bus.publish(event3)
    
    # Get causation chain
    chain = event_bus.get_causation_chain(event3_id)
    
    assert len(chain) == 3
    assert chain[0].type == EventType.SCENE_WRITTEN
    assert chain[1].type == EventType.SHOT_PLANNED
    assert chain[2].type == EventType.IMAGE_GENERATED


@pytest.mark.asyncio
async def test_event_replay(event_bus):
    """Test event replay functionality"""
    project_id = "PROJ-TEST-REPLAY"
    
    # Publish multiple events
    events_to_publish = [
        Event(project_id=project_id, type=EventType.PROJECT_CREATED, actor="System"),
        Event(project_id=project_id, type=EventType.SCENE_WRITTEN, actor="ScriptWriter"),
        Event(project_id=project_id, type=EventType.SHOT_PLANNED, actor="ShotDirector"),
    ]
    
    for event in events_to_publish:
        await event_bus.publish(event)
    
    await asyncio.sleep(0.2)
    
    # Replay events
    replayed_events = await event_bus.replay_events(project_id)
    
    assert len(replayed_events) >= 3
    assert all(e.project_id == project_id for e in replayed_events)


@pytest.mark.asyncio
async def test_unsubscribe(event_bus):
    """Test unsubscribing from events"""
    subscriber = TestSubscriber("TestAgent")
    
    # Subscribe
    event_bus.subscribe(subscriber, [EventType.PROJECT_CREATED])
    
    # Publish event - should receive
    event1 = Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="System"
    )
    await event_bus.publish(event1)
    await asyncio.sleep(0.1)
    
    assert len(subscriber.received_events) == 1
    
    # Unsubscribe
    event_bus.unsubscribe(subscriber, [EventType.PROJECT_CREATED])
    
    # Publish another event - should not receive
    event2 = Event(
        project_id="PROJ-002",
        type=EventType.PROJECT_CREATED,
        actor="System"
    )
    await event_bus.publish(event2)
    await asyncio.sleep(0.1)
    
    # Should still have only 1 event
    assert len(subscriber.received_events) == 1


@pytest.mark.asyncio
async def test_event_filtering(event_bus):
    """Test that subscribers only receive subscribed event types"""
    subscriber = TestSubscriber("TestAgent")
    
    # Subscribe only to IMAGE_GENERATED
    event_bus.subscribe(subscriber, [EventType.IMAGE_GENERATED])
    
    # Publish different event types
    await event_bus.publish(Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="System"
    ))
    
    await event_bus.publish(Event(
        project_id="PROJ-001",
        type=EventType.IMAGE_GENERATED,
        actor="ImageGenAgent"
    ))
    
    await event_bus.publish(Event(
        project_id="PROJ-001",
        type=EventType.SCENE_WRITTEN,
        actor="ScriptWriter"
    ))
    
    await asyncio.sleep(0.1)
    
    # Should only receive IMAGE_GENERATED event
    assert len(subscriber.received_events) == 1
    assert subscriber.received_events[0].type == EventType.IMAGE_GENERATED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
