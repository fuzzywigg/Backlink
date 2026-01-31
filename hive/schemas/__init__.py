"""
Pydantic schemas for type safety and validation across the Backlink Hive.

This module provides comprehensive data validation for:
- Honeycomb state management
- API requests and responses
- Payment processing
- Task management
- Bee work results
"""

from hive.schemas.api import (
    APIErrorResponse,
    APISuccessResponse,
    BeeSpawnRequest,
    BeeSpawnResponse,
    EventTriggerRequest,
    HealthCheckResponse,
    TaskCreateRequest,
)
from hive.schemas.base import (
    BaseSchema,
    MetadataSchema,
    TimestampedSchema,
)
from hive.schemas.bee import (
    BeeCategory,
    BeeConfig,
    BeeRole,
    BeeStatus,
    BeeWorkResult,
)
from hive.schemas.honeycomb import (
    BeeMetadata,
    HoneycombStateSchema,
    IntelSchema,
    TaskPriority,
    TaskSchema,
    TaskStatus,
    WisdomEntrySchema,
    WisdomSchema,
)
from hive.schemas.payment import (
    PaymentIntentSchema,
    PaymentMethodSchema,
    PaymentProvider,
    PaymentStatus,
    TransactionSchema,
    WalletSchema,
)

__all__ = [
    # Base
    "BaseSchema",
    "MetadataSchema",
    "TimestampedSchema",
    # Honeycomb
    "BeeMetadata",
    "HoneycombStateSchema",
    "IntelSchema",
    "TaskSchema",
    "TaskStatus",
    "TaskPriority",
    "WisdomSchema",
    "WisdomEntrySchema",
    # API
    "APIErrorResponse",
    "APISuccessResponse",
    "BeeSpawnRequest",
    "BeeSpawnResponse",
    "EventTriggerRequest",
    "HealthCheckResponse",
    "TaskCreateRequest",
    # Payment
    "PaymentIntentSchema",
    "PaymentMethodSchema",
    "PaymentProvider",
    "PaymentStatus",
    "TransactionSchema",
    "WalletSchema",
    # Bee
    "BeeWorkResult",
    "BeeConfig",
    "BeeStatus",
    "BeeRole",
    "BeeCategory",
]
