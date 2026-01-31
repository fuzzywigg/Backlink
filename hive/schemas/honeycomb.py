"""
Honeycomb schemas for state, intel, tasks, and wisdom.

The honeycomb is the shared memory of the hive where bees
communicate indirectly via stigmergy.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from hive.schemas.base import BaseSchema, MetadataSchema, TimestampedSchema


class TaskStatus(str, Enum):
    """Status of a task in the queue."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Priority level for task scheduling."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class BeeMetadata(BaseSchema):
    """Metadata about bee activity."""

    last_updated: datetime
    last_updated_by: str
    version: str = "1.0"


class TaskSchema(TimestampedSchema):
    """Schema for tasks in the task queue."""

    task_id: str = Field(..., description="Unique task identifier")
    bee_type: str = Field(..., description="Type of bee that should handle this task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")
    payload: dict[str, Any] = Field(default_factory=dict, description="Task-specific data")
    result: dict[str, Any] | None = Field(None, description="Result of task execution")
    error: str | None = Field(None, description="Error message if task failed")
    assigned_to: str | None = Field(None, description="Bee instance handling this task")
    started_at: datetime | None = Field(None, description="When task execution started")
    completed_at: datetime | None = Field(None, description="When task completed")

    @field_validator("task_id")
    @classmethod
    def validate_task_id(cls, v: str) -> str:
        """Ensure task_id is non-empty."""
        if not v or not v.strip():
            raise ValueError("task_id must be a non-empty string")
        return v.strip()


class IntelSchema(TimestampedSchema):
    """Schema for intelligence gathered by scout bees."""

    intel_id: str = Field(..., description="Unique intel identifier")
    source: str = Field(..., description="Source of intelligence (bee type or external)")
    category: str = Field(..., description="Category of intelligence")
    data: dict[str, Any] = Field(..., description="Intelligence data")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    tags: list[str] = Field(default_factory=list, description="Searchable tags")
    expires_at: datetime | None = Field(
        None, description="Expiration timestamp for time-sensitive intel"
    )


class WisdomEntrySchema(TimestampedSchema):
    """Schema for long-term knowledge entries."""

    entry_id: str = Field(..., description="Unique entry identifier")
    category: str = Field(..., description="Knowledge category")
    content: dict[str, Any] = Field(..., description="Knowledge content")
    learned_from: list[str] = Field(
        default_factory=list, description="Sources that contributed to this wisdom"
    )
    usage_count: int = Field(default=0, ge=0, description="Times this wisdom was used")
    last_used: datetime | None = Field(None, description="Last time wisdom was accessed")


class WisdomSchema(BaseSchema):
    """Schema for the wisdom honeycomb file."""

    entries: list[WisdomEntrySchema] = Field(default_factory=list, description="Wisdom entries")
    meta: MetadataSchema = Field(
        default_factory=MetadataSchema, description="File metadata", alias="_meta"
    )


class HoneycombStateSchema(BaseSchema):
    """
    Schema for the main honeycomb state.json file.

    This is the primary communication channel between bees.
    """

    # Core broadcast state
    current_track: dict[str, Any] | None = Field(None, description="Currently playing track")
    queue: list[dict[str, Any]] = Field(default_factory=list, description="Upcoming tracks")
    listeners: dict[str, Any] = Field(default_factory=dict, description="Current listener data")

    # Recent bee activity
    recent_intel: list[dict[str, Any]] = Field(
        default_factory=list, description="Recent intelligence"
    )
    active_events: list[dict[str, Any]] = Field(default_factory=list, description="Active events")

    # System status
    stream_status: dict[str, Any] = Field(default_factory=dict, description="Stream health metrics")
    treasury_status: dict[str, Any] = Field(default_factory=dict, description="Financial status")

    # Metadata
    meta: MetadataSchema = Field(
        default_factory=MetadataSchema, description="State metadata", alias="_meta"
    )

    model_config = {
        "extra": "allow",  # Allow extra fields for extensibility
        "populate_by_name": True,  # Allow using alias or field name
    }
