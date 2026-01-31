"""
Validation layer for honeycomb data operations.

This module provides validation wrappers around the state manager
to ensure data integrity and type safety.
"""

from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from hive.schemas.honeycomb import HoneycombStateSchema, IntelSchema, TaskSchema, WisdomSchema
from hive.utils.feature_flags import is_feature_enabled
from hive.utils.state_manager import StateManager

# Re-export ValidationError for convenience
ValidationError = PydanticValidationError


class ValidatedStateManager:
    """
    StateManager wrapper with Pydantic validation.

    When validation_layer feature flag is enabled, this enforces
    schema validation on all honeycomb operations.
    """

    def __init__(self, hive_path: Path | None = None, strict: bool = False) -> None:
        """
        Initialize validated state manager.

        Args:
            hive_path: Path to hive directory
            strict: If True, always validate. If False, use feature flag.
        """
        self.state_manager = StateManager(hive_path)
        self.strict = strict

    def _should_validate(self) -> bool:
        """Check if validation should be performed."""
        return self.strict or is_feature_enabled("validation_layer")

    def read_state(self) -> dict[str, Any]:
        """Read state with optional validation."""
        data = self.state_manager.read_state()

        if self._should_validate() and data:
            try:
                # Validate against schema
                validated = HoneycombStateSchema(**data)
                return validated.model_dump(exclude_none=True)
            except ValidationError as e:
                print(f"State validation warning: {e}")
                # In non-strict mode, return data anyway
                if not self.strict:
                    return data
                raise

        return data

    def write_state(
        self, state_data: dict[str, Any], bee_type: str, validate: bool = True
    ) -> None:
        """
        Write state with optional validation.

        Args:
            state_data: State data to write
            bee_type: Type of bee writing the state
            validate: Whether to validate before writing
        """
        if validate and self._should_validate():
            try:
                # Validate against schema
                validated = HoneycombStateSchema(**state_data)
                state_data = validated.model_dump(exclude_none=True)
            except ValidationError as e:
                print(f"State validation error: {e}")
                if self.strict:
                    raise
                # In non-strict mode, continue with unvalidated data

        self.state_manager.write_state(state_data, bee_type)

    def validate_intel(self, intel_data: dict[str, Any]) -> IntelSchema:
        """
        Validate intel data against schema.

        Args:
            intel_data: Intel data to validate

        Returns:
            Validated IntelSchema instance

        Raises:
            ValidationError: If validation fails
        """
        return IntelSchema(**intel_data)

    def validate_task(self, task_data: dict[str, Any]) -> TaskSchema:
        """
        Validate task data against schema.

        Args:
            task_data: Task data to validate

        Returns:
            Validated TaskSchema instance

        Raises:
            ValidationError: If validation fails
        """
        return TaskSchema(**task_data)

    def validate_wisdom(self, wisdom_data: dict[str, Any]) -> WisdomSchema:
        """
        Validate wisdom data against schema.

        Args:
            wisdom_data: Wisdom data to validate

        Returns:
            Validated WisdomSchema instance

        Raises:
            ValidationError: If validation fails
        """
        return WisdomSchema(**wisdom_data)


def create_validated_state_manager(
    hive_path: Path | None = None, strict: bool = False
) -> ValidatedStateManager:
    """
    Factory function to create a validated state manager.

    Args:
        hive_path: Path to hive directory
        strict: Whether to enforce strict validation

    Returns:
        ValidatedStateManager instance
    """
    return ValidatedStateManager(hive_path=hive_path, strict=strict)
