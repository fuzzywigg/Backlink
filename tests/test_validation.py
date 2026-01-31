"""
Tests for validation layer.
"""

import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from hive.schemas import IntelSchema, TaskSchema, WisdomSchema
from hive.utils.validation import ValidatedStateManager


@pytest.fixture
def temp_hive_path():
    """Create a temporary hive directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hive_path = Path(tmpdir) / "hive"
        hive_path.mkdir()
        honeycomb_path = hive_path / "honeycomb"
        honeycomb_path.mkdir()
        yield hive_path


@pytest.fixture
def validated_manager(temp_hive_path, monkeypatch):
    """Create a validated state manager in dev mode."""
    # Set development mode to avoid secret key requirement
    monkeypatch.setenv("ENVIRONMENT", "dev")
    return ValidatedStateManager(hive_path=temp_hive_path, strict=False)


@pytest.fixture
def strict_manager(temp_hive_path, monkeypatch):
    """Create a strict validated state manager."""
    monkeypatch.setenv("ENVIRONMENT", "dev")
    return ValidatedStateManager(hive_path=temp_hive_path, strict=True)


class TestValidatedStateManager:
    """Tests for ValidatedStateManager."""

    def test_initialization(self, validated_manager):
        """Test manager initializes correctly."""
        assert validated_manager is not None
        assert validated_manager.state_manager is not None

    def test_read_empty_state(self, validated_manager):
        """Test reading empty state."""
        state = validated_manager.read_state()
        assert state == {}

    def test_write_and_read_valid_state(self, validated_manager):
        """Test writing and reading valid state."""
        state_data = {
            "current_track": {"title": "Test Track"},
            "queue": [],
            "listeners": {},
        }

        validated_manager.write_state(state_data, "test_bee")

        # Read it back
        read_state = validated_manager.read_state()

        assert read_state["current_track"]["title"] == "Test Track"

    def test_write_invalid_state_non_strict(self, validated_manager):
        """Test that invalid state is accepted in non-strict mode."""
        # This would be invalid according to schema
        invalid_state = {
            "current_track": "not a dict",  # Should be dict
        }

        # Should not raise in non-strict mode
        validated_manager.write_state(invalid_state, "test_bee", validate=True)

    def test_write_invalid_state_strict(self, strict_manager):
        """Test that invalid state is rejected in strict mode."""
        invalid_state = {
            "current_track": "not a dict",
            "queue": "not a list",
        }

        # Should raise in strict mode
        with pytest.raises(ValidationError):
            strict_manager.write_state(invalid_state, "test_bee", validate=True)

    def test_write_without_validation(self, validated_manager):
        """Test writing without validation."""
        invalid_state = {
            "completely": "invalid",
        }

        # Should work when validation is disabled
        validated_manager.write_state(invalid_state, "test_bee", validate=False)

    def test_validate_intel(self, validated_manager):
        """Test validating intel data."""
        intel_data = {
            "intel_id": "intel_123",
            "source": "trend_scout",
            "category": "trends",
            "data": {"info": "value"},
        }

        intel = validated_manager.validate_intel(intel_data)

        assert isinstance(intel, IntelSchema)
        assert intel.intel_id == "intel_123"

    def test_validate_invalid_intel(self, validated_manager):
        """Test validating invalid intel raises error."""
        invalid_intel = {
            "intel_id": "intel_123",
            # Missing required fields
        }

        with pytest.raises(ValidationError):
            validated_manager.validate_intel(invalid_intel)

    def test_validate_task(self, validated_manager):
        """Test validating task data."""
        task_data = {
            "task_id": "task_123",
            "bee_type": "trend_scout",
            "priority": "high",
        }

        task = validated_manager.validate_task(task_data)

        assert isinstance(task, TaskSchema)
        assert task.task_id == "task_123"

    def test_validate_wisdom(self, validated_manager):
        """Test validating wisdom data."""
        wisdom_data = {
            "entries": [
                {
                    "entry_id": "wisdom_1",
                    "category": "music",
                    "content": {"data": "value"},
                }
            ]
        }

        wisdom = validated_manager.validate_wisdom(wisdom_data)

        assert isinstance(wisdom, WisdomSchema)
        assert len(wisdom.entries) == 1


class TestFeatureFlagIntegration:
    """Tests for feature flag integration with validation."""

    def test_validation_respects_feature_flag(self, validated_manager, monkeypatch):
        """Test that validation can be controlled by feature flag."""
        # Disable validation feature
        monkeypatch.setenv("FEATURE_VALIDATION_LAYER", "false")

        # Invalid state should be accepted when validation is off
        invalid_state = {"invalid": "structure"}

        # Should not raise
        validated_manager.write_state(invalid_state, "test_bee")

    def test_strict_mode_overrides_feature_flag(self, strict_manager, monkeypatch):
        """Test that strict mode enforces validation regardless of feature flag."""
        # Disable validation feature
        monkeypatch.setenv("FEATURE_VALIDATION_LAYER", "false")

        # Create truly invalid data that will fail Pydantic validation
        # Use required fields with wrong types
        from pydantic import ValidationError as PydanticValidationError

        # Try to validate an invalid task directly
        invalid_task = {
            "task_id": "",  # Empty task_id should fail validation
            "bee_type": "test",
        }

        # Should raise validation error in strict mode despite feature flag being off
        with pytest.raises(PydanticValidationError):
            strict_manager.validate_task(invalid_task)


class TestStateManagerMetadata:
    """Tests for state metadata handling."""

    def test_metadata_added_on_write(self, validated_manager):
        """Test that metadata is added when writing state."""
        state_data = {
            "current_track": {"title": "Test"},
        }

        validated_manager.write_state(state_data, "test_bee")

        # Get the raw data directly from state manager
        raw_state = validated_manager.state_manager.read_state()

        # Check for _meta in raw state (before schema conversion)
        assert "_meta" in raw_state
        assert "last_updated_by" in raw_state["_meta"]
        assert raw_state["_meta"]["last_updated_by"] == "test_bee"

    def test_metadata_preserved_on_update(self, validated_manager):
        """Test that metadata is updated on subsequent writes."""
        # First write
        state_data = {"current_track": {"title": "Track 1"}}
        validated_manager.write_state(state_data, "bee_1")

        # Second write
        state_data["current_track"]["title"] = "Track 2"
        validated_manager.write_state(state_data, "bee_2")

        # Get raw state to check metadata
        raw_state = validated_manager.state_manager.read_state()

        assert raw_state["_meta"]["last_updated_by"] == "bee_2"


class TestValidatedStateManagerFactory:
    """Tests for factory function."""

    def test_create_validated_state_manager(self, temp_hive_path, monkeypatch):
        """Test factory function creates manager."""
        monkeypatch.setenv("ENVIRONMENT", "dev")

        from hive.utils.validation import create_validated_state_manager

        manager = create_validated_state_manager(hive_path=temp_hive_path)

        assert isinstance(manager, ValidatedStateManager)

    def test_create_strict_manager(self, temp_hive_path, monkeypatch):
        """Test factory function creates strict manager."""
        monkeypatch.setenv("ENVIRONMENT", "dev")

        from hive.utils.validation import create_validated_state_manager

        manager = create_validated_state_manager(hive_path=temp_hive_path, strict=True)

        assert manager.strict is True
