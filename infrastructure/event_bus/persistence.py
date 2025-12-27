"""
Event persistence layer for storing events to database.

This module provides functionality to persist events to PostgreSQL
for long-term storage, auditing, and analytics.
"""

import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from ..blackboard.blackboard import SharedBlackboard
from .event import Event, EventType


logger = logging.getLogger(__name__)


class EventPersistence:
    """
    Event persistence layer for storing events to database.
    
    Features:
    - Store events to PostgreSQL
    - Query events by project, time range, type
    - Event retention management
    - Causation chain reconstruction
    """
    
    def __init__(self, blackboard: SharedBlackboard):
        """
        Initialize event persistence.
        
        Args:
            blackboard: Shared Blackboard instance for database access
        """
        self.blackboard = blackboard
    
    async def persist_event(self, event: Event) -> bool:
        """
        Persist an event to the database.
        
        Args:
            event: Event to persist
            
        Returns:
            bool: True if successful
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO events (
                    event_id, project_id, event_type, actor,
                    causation_id, timestamp, payload,
                    blackboard_pointer, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    event.event_id,
                    event.project_id,
                    event.type.value,
                    event.actor,
                    event.causation_id,
                    event.timestamp,
                    json.dumps(event.payload),
                    event.blackboard_pointer,
                    json.dumps(event.metadata)
                )
            )
            
            conn.commit()
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            logger.debug(f"Persisted event {event.event_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to persist event {event.event_id}: {e}")
            return False
    
    async def get_events(
        self,
        project_id: Optional[str] = None,
        event_types: Optional[List[EventType]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Event]:
        """
        Query events from database.
        
        Args:
            project_id: Filter by project ID
            event_types: Filter by event types
            start_time: Start time filter
            end_time: End time filter
            limit: Maximum number of events to return
            
        Returns:
            List of events matching criteria
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if project_id:
                query += " AND project_id = %s"
                params.append(project_id)
            
            if event_types:
                query += " AND event_type = ANY(%s)"
                params.append([et.value for et in event_types])
            
            if start_time:
                query += " AND timestamp >= %s"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= %s"
                params.append(end_time.isoformat())
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            # Convert rows to Event objects
            events = []
            for row in rows:
                event = Event(
                    event_id=row[0],
                    project_id=row[1],
                    type=EventType(row[2]),
                    actor=row[3],
                    causation_id=row[4],
                    timestamp=row[5],
                    payload=json.loads(row[6]) if row[6] else {},
                    blackboard_pointer=row[7],
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to query events: {e}")
            return []
    
    async def get_causation_chain(self, event_id: str) -> List[Event]:
        """
        Reconstruct causation chain from database.
        
        Args:
            event_id: Event ID to trace
            
        Returns:
            List of events in causation chain (oldest to newest)
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            # Recursive CTE to trace causation chain
            query = """
                WITH RECURSIVE causation_chain AS (
                    -- Base case: start with the given event
                    SELECT * FROM events WHERE event_id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: find parent events
                    SELECT e.*
                    FROM events e
                    INNER JOIN causation_chain cc ON e.event_id = cc.causation_id
                )
                SELECT * FROM causation_chain
                ORDER BY timestamp ASC
            """
            
            cursor.execute(query, (event_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            # Convert to Event objects
            events = []
            for row in rows:
                event = Event(
                    event_id=row[0],
                    project_id=row[1],
                    type=EventType(row[2]),
                    actor=row[3],
                    causation_id=row[4],
                    timestamp=row[5],
                    payload=json.loads(row[6]) if row[6] else {},
                    blackboard_pointer=row[7],
                    metadata=json.loads(row[8]) if row[8] else {}
                )
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get causation chain: {e}")
            return []
    
    async def cleanup_old_events(self, retention_days: int = 30) -> int:
        """
        Clean up events older than retention period.
        
        Args:
            retention_days: Number of days to retain events
            
        Returns:
            Number of events deleted
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            cursor.execute(
                """
                DELETE FROM events
                WHERE timestamp < %s
                RETURNING event_id
                """,
                (cutoff_date.isoformat(),)
            )
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            logger.info(f"Cleaned up {deleted_count} old events")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old events: {e}")
            return 0
    
    async def get_event_statistics(
        self,
        project_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """
        Get event statistics for a project.
        
        Args:
            project_id: Project ID
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Dictionary with event statistics
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    event_type,
                    COUNT(*) as count,
                    AVG((metadata->>'cost')::numeric) as avg_cost,
                    AVG((metadata->>'latency_ms')::numeric) as avg_latency
                FROM events
                WHERE project_id = %s
            """
            params = [project_id]
            
            if start_time:
                query += " AND timestamp >= %s"
                params.append(start_time.isoformat())
            
            if end_time:
                query += " AND timestamp <= %s"
                params.append(end_time.isoformat())
            
            query += " GROUP BY event_type"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            statistics = {}
            for row in rows:
                statistics[row[0]] = {
                    "count": row[1],
                    "avg_cost": float(row[2]) if row[2] else 0.0,
                    "avg_latency_ms": float(row[3]) if row[3] else 0.0
                }
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to get event statistics: {e}")
            return {}
