"""
API request and response schemas for the Hive REST API.
"""

from typing import Any, Literal

from pydantic import Field

from hive.schemas.base import BaseSchema, TimestampedSchema


class APISuccessResponse(BaseSchema):
    """Standard success response format."""

    status: Literal["success"] = "success"
    message: str = Field(..., description="Human-readable success message")
    data: dict[str, Any] | None = Field(None, description="Response data")


class APIErrorResponse(BaseSchema):
    """Standard error response format."""

    status: Literal["error"] = "error"
    message: str = Field(..., description="Human-readable error message")
    error_code: str | None = Field(None, description="Machine-readable error code")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class HealthCheckResponse(BaseSchema):
    """Health check endpoint response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., ge=0, description="Service uptime in seconds")
    hive_status: dict[str, Any] = Field(default_factory=dict, description="Hive operational status")
    git_sha: str = Field(
        default="unknown",
        description="Non-secret git/source SHA from build env (GIT_SHA/SOURCE_COMMIT/COMMIT_SHA)",
    )
    build_id: str | None = Field(
        default=None,
        description="Optional CI/CD build identifier from BUILD_ID",
    )
    build_time: str | None = Field(
        default=None,
        description="Optional build timestamp from BUILD_TIME or BUILD_TIMESTAMP",
    )


class BeeSpawnRequest(BaseSchema):
    """Request to spawn a specific bee."""

    bee_type: str = Field(..., description="Type of bee to spawn")
    task_data: dict[str, Any] | None = Field(None, description="Optional task data for the bee")


class BeeSpawnResponse(TimestampedSchema):
    """Response from spawning a bee."""

    bee_type: str
    status: Literal["spawned", "failed"]
    result: dict[str, Any] | None = None
    error: str | None = None


class EventTriggerRequest(BaseSchema):
    """Request to trigger a hive event."""

    event_type: str = Field(..., description="Type of event to trigger")
    data: dict[str, Any] = Field(default_factory=dict, description="Event-specific data")


class TaskCreateRequest(BaseSchema):
    """Request to create a new task."""

    bee_type: str = Field(..., description="Type of bee to assign task to")
    priority: Literal["low", "medium", "high", "urgent"] = "medium"
    payload: dict[str, Any] = Field(default_factory=dict, description="Task payload")
