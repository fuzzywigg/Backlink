"""
Bee-specific schemas for configuration and work results.
"""

from enum import Enum
from typing import Any

from pydantic import Field

from hive.schemas.base import BaseSchema, TimestampedSchema


class BeeRole(str, Enum):
    """Bee role in ABC pattern."""

    SCOUT = "scout"
    EMPLOYED = "employed"
    ONLOOKER = "onlooker"


class BeeCategory(str, Enum):
    """Bee functional category."""

    CONTENT = "content"
    RESEARCH = "research"
    MARKETING = "marketing"
    MONETIZATION = "monetization"
    COMMUNITY = "community"
    TECHNICAL = "technical"
    SYSTEM = "system"


class BeeStatus(str, Enum):
    """Bee operational status."""

    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    SLEEPING = "sleeping"


class BeeConfig(BaseSchema):
    """Configuration for a bee instance."""

    bee_type: str = Field(..., description="Unique bee type identifier")
    bee_name: str = Field(..., description="Human-readable bee name")
    category: BeeCategory
    role: BeeRole = Field(default=BeeRole.SCOUT, description="ABC role")
    enabled: bool = Field(default=True, description="Whether bee is enabled")
    schedule: dict[str, Any] | None = Field(None, description="Scheduling configuration")
    config: dict[str, Any] = Field(default_factory=dict, description="Bee-specific configuration")


class BeeWorkResult(TimestampedSchema):
    """Result of bee work execution."""

    bee_type: str = Field(..., description="Type of bee that performed work")
    status: BeeStatus
    success: bool = Field(..., description="Whether work was successful")
    data: dict[str, Any] = Field(default_factory=dict, description="Work result data")
    error: str | None = Field(None, description="Error message if failed")
    intel_generated: list[str] = Field(
        default_factory=list, description="IDs of intel entries created"
    )
    tasks_spawned: list[str] = Field(default_factory=list, description="IDs of tasks created")
    execution_time_ms: float | None = Field(
        None, ge=0, description="Execution time in milliseconds"
    )
