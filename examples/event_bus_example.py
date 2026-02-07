"""
Example usage of the Event Bus system.

This example demonstrates:
1. Creating an Event Bus
2. Subscribing agents to events
3. Publishing events
4. Causation tracking
5. Event replay
"""

import asyncio
import logging
from src.infrastructure.event_bus import EventBus, Event, EventType, EventSubscriber

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScriptWriterAgent(EventSubscriber):
    """Example ScriptWriter Agent"""
    
    def __init__(self):
        super().__init__("ScriptWriter")
    
    async def handle_event(self, event: Event) -> None:
        """Handle PROJECT_CREATED event"""
        if event.type == EventType.PROJECT_CREATED:
            logger.info(f"ScriptWriter received PROJECT_CREATED for {event.project_id}")
            
            # Simulate script writing
            await asyncio.sleep(1)
            
            # Publish SCENE_WRITTEN event
            scene_event = Event(
                project_id=event.project_id,
                type=EventType.SCENE_WRITTEN,
                actor=self.name,
                causation_id=event.event_id,
                payload={
                    "scenes": [
                        {"description": "Girl walking in rain"},
                        {"description": "Meets stranger with umbrella"}
                    ]
                }
            )
            
            # Get event bus from context (in real implementation)
            # await event_bus.publish(scene_event)
            logger.info(f"ScriptWriter would publish SCENE_WRITTEN")


class ShotDirectorAgent(EventSubscriber):
    """Example ShotDirector Agent"""
    
    def __init__(self):
        super().__init__("ShotDirector")
    
    async def handle_event(self, event: Event) -> None:
        """Handle SCENE_WRITTEN event"""
        if event.type == EventType.SCENE_WRITTEN:
            logger.info(f"ShotDirector received SCENE_WRITTEN for {event.project_id}")
            
            # Simulate shot planning
            await asyncio.sleep(1)
            
            # Publish SHOT_PLANNED event
            logger.info(f"ShotDirector would publish SHOT_PLANNED")


class ImageGenAgent(EventSubscriber):
    """Example ImageGen Agent"""
    
    def __init__(self):
        super().__init__("ImageGenAgent")
    
    async def handle_event(self, event: Event) -> None:
        """Handle KEYFRAME_REQUESTED event"""
        if event.type == EventType.KEYFRAME_REQUESTED:
            logger.info(f"ImageGenAgent received KEYFRAME_REQUESTED for {event.project_id}")
            
            # Simulate image generation
            await asyncio.sleep(2)
            
            # Publish IMAGE_GENERATED event
            logger.info(f"ImageGenAgent would publish IMAGE_GENERATED")


class ArtDirectorAgent(EventSubscriber):
    """Example ArtDirector Agent"""
    
    def __init__(self):
        super().__init__("ArtDirector")
    
    async def handle_event(self, event: Event) -> None:
        """Handle IMAGE_GENERATED event"""
        if event.type == EventType.IMAGE_GENERATED:
            logger.info(f"ArtDirector received IMAGE_GENERATED for {event.project_id}")
            
            # Simulate feature extraction
            await asyncio.sleep(0.5)
            
            # Publish DNA_BANK_UPDATED event
            logger.info(f"ArtDirector would publish DNA_BANK_UPDATED")


async def main():
    """Main example function"""
    
    # 1. Create and connect Event Bus
    logger.info("=== Creating Event Bus ===")
    event_bus = EventBus(redis_url="redis://localhost:6379")
    await event_bus.connect()
    
    try:
        # 2. Create agents
        logger.info("\n=== Creating Agents ===")
        script_writer = ScriptWriterAgent()
        shot_director = ShotDirectorAgent()
        image_gen = ImageGenAgent()
        art_director = ArtDirectorAgent()
        
        # 3. Subscribe agents to events
        logger.info("\n=== Subscribing Agents ===")
        event_bus.subscribe(script_writer, [EventType.PROJECT_CREATED])
        event_bus.subscribe(shot_director, [EventType.SCENE_WRITTEN])
        event_bus.subscribe(image_gen, [EventType.KEYFRAME_REQUESTED])
        event_bus.subscribe(art_director, [EventType.IMAGE_GENERATED])
        
        # 4. Publish initial event
        logger.info("\n=== Publishing PROJECT_CREATED Event ===")
        project_event = Event(
            project_id="PROJ-EXAMPLE-001",
            type=EventType.PROJECT_CREATED,
            actor="RequirementParser",
            payload={
                "title": "Rain and Warmth",
                "duration": 30,
                "quality_tier": "balanced"
            }
        )
        
        event_id = await event_bus.publish(project_event)
        logger.info(f"Published event: {event_id}")
        
        # Wait for event processing
        await asyncio.sleep(2)
        
        # 5. Publish follow-up events to demonstrate chain
        logger.info("\n=== Publishing Follow-up Events ===")
        
        scene_event = Event(
            project_id="PROJ-EXAMPLE-001",
            type=EventType.SCENE_WRITTEN,
            actor="ScriptWriter",
            causation_id=event_id,
            payload={"scenes": ["Scene 1", "Scene 2"]}
        )
        scene_event_id = await event_bus.publish(scene_event)
        
        await asyncio.sleep(1)
        
        keyframe_event = Event(
            project_id="PROJ-EXAMPLE-001",
            type=EventType.KEYFRAME_REQUESTED,
            actor="ShotDirector",
            causation_id=scene_event_id,
            payload={"shot_id": "S01"}
        )
        keyframe_event_id = await event_bus.publish(keyframe_event)
        
        await asyncio.sleep(2)
        
        image_event = Event(
            project_id="PROJ-EXAMPLE-001",
            type=EventType.IMAGE_GENERATED,
            actor="ImageGenAgent",
            causation_id=keyframe_event_id,
            payload={"artifact_url": "s3://example/image.png"}
        )
        image_event_id = await event_bus.publish(image_event)
        
        await asyncio.sleep(1)
        
        # 6. Demonstrate causation tracking
        logger.info("\n=== Causation Chain ===")
        chain = event_bus.get_causation_chain(image_event_id)
        logger.info(f"Causation chain length: {len(chain)}")
        for i, event in enumerate(chain):
            logger.info(f"  {i+1}. {event.type.value} by {event.actor}")
        
        # 7. Demonstrate event replay
        logger.info("\n=== Event Replay ===")
        replayed_events = await event_bus.replay_events("PROJ-EXAMPLE-001")
        logger.info(f"Replayed {len(replayed_events)} events")
        for event in replayed_events:
            logger.info(f"  - {event.type.value} at {event.timestamp}")
        
        # 8. Get all project events
        logger.info("\n=== Project Events ===")
        project_events = await event_bus.get_project_events("PROJ-EXAMPLE-001")
        logger.info(f"Total events for project: {len(project_events)}")
        
    finally:
        # Cleanup
        logger.info("\n=== Disconnecting ===")
        await event_bus.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
