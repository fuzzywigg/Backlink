"""
Base schemas for the Backlink Hive.

Provides common base classes and utilities for all schemas.
"""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        # Allow arbitrary types for compatibility with legacy code
        arbitrary_types_allowed=True,
        # Validate on assignment
        validate_assignment=True,
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Extra fields forbidden by default
        extra="forbid",
        # Populate by field name
        populate_by_name=True,
    )


class TimestampedSchema(BaseSchema):
    """Schema with automatic timestamp tracking."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this object was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this object was last updated",
    )

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now(timezone.utc)


class MetadataSchema(BaseSchema):
    """Generic metadata schema for extensibility."""

    last_updated: datetime | None = Field(
        None, description="Last update timestamp (ISO format)"
    )
    last_updated_by: str | None = Field(None, description="Identifier of last updater")
    version: str = Field(default="1.0", description="Schema version")
    extra: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata fields"
    )
