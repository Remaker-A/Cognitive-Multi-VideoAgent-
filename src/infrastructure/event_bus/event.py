"""
Event data model and types for the Event Bus system.
"""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class EventType(str, Enum):
    """All event types in the system"""
    # Project lifecycle
    PROJECT_CREATED = "PROJECT_CREATED"
    PROJECT_FINALIZED = "PROJECT_FINALIZED"
    
    # Script and planning
    SCENE_WRITTEN = "SCENE_WRITTEN"
    SHOT_PLANNED = "SHOT_PLANNED"
    
    # Image generation
    KEYFRAME_REQUESTED = "KEYFRAME_REQUESTED"
    IMAGE_GENERATED = "IMAGE_GENERATED"
    
    # DNA and prompts
    DNA_BANK_UPDATED = "DNA_BANK_UPDATED"
    PROMPT_ADJUSTMENT = "PROMPT_ADJUSTMENT"
    
    # Video generation
    PREVIEW_VIDEO_REQUESTED = "PREVIEW_VIDEO_REQUESTED"
    PREVIEW_VIDEO_READY = "PREVIEW_VIDEO_READY"
    FINAL_VIDEO_REQUESTED = "FINAL_VIDEO_REQUESTED"
    FINAL_VIDEO_READY = "FINAL_VIDEO_READY"
    
    # QA and consistency
    QA_REPORT = "QA_REPORT"
    CONSISTENCY_FAILED = "CONSISTENCY_FAILED"
    
    # Audio
    MUSIC_COMPOSED = "MUSIC_COMPOSED"
    VOICE_RENDERED = "VOICE_RENDERED"
    
    # Approval
    SHOT_APPROVED = "SHOT_APPROVED"
    
    # User approval
    USER_APPROVAL_REQUIRED = "USER_APPROVAL_REQUIRED"
    USER_APPROVED = "USER_APPROVED"
    USER_REVISION_REQUESTED = "USER_REVISION_REQUESTED"
    USER_REJECTED = "USER_REJECTED"
    
    # Error handling
    HUMAN_GATE_TRIGGERED = "HUMAN_GATE_TRIGGERED"
    COST_OVERRUN_WARNING = "COST_OVERRUN_WARNING"
    
    # Image editing
    IMAGE_EDIT_REQUESTED = "IMAGE_EDIT_REQUESTED"
    IMAGE_EDITED = "IMAGE_EDITED"
    
    # Error correction
    ERROR_DETECTED = "ERROR_DETECTED"
    ERROR_CORRECTED = "ERROR_CORRECTED"
    ERROR_CORRECTION_REQUESTED = "ERROR_CORRECTION_REQUESTED"
    USER_ERROR_REPORTED = "USER_ERROR_REPORTED"


@dataclass
class Event:
    """
    Standard event format for the Event Bus.
    
    All events must follow this structure to ensure consistency
    and enable proper causation tracking.
    """
    event_id: str = field(default_factory=lambda: f"EV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}")
    project_id: str = ""
    type: EventType = EventType.PROJECT_CREATED
    actor: str = ""  # Agent name that published the event
    causation_id: Optional[str] = None  # ID of the event that caused this event
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    payload: Dict[str, Any] = field(default_factory=dict)
    blackboard_pointer: Optional[str] = None  # Path to related data in Blackboard
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "actor": self.actor,
            "causation_id": self.causation_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "blackboard_pointer": self.blackboard_pointer,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary"""
        event_type = EventType(data["type"]) if isinstance(data["type"], str) else data["type"]
        return cls(
            event_id=data.get("event_id", ""),
            project_id=data.get("project_id", ""),
            type=event_type,
            actor=data.get("actor", ""),
            causation_id=data.get("causation_id"),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            payload=data.get("payload", {}),
            blackboard_pointer=data.get("blackboard_pointer"),
            metadata=data.get("metadata", {})
        )
