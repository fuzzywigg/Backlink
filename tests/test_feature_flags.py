"""
Tests for feature flags system.
"""

import json
import tempfile
from pathlib import Path

import pytest

from hive.utils.feature_flags import (
    FeatureFlag,
    FeatureFlagManager,
    FeatureStatus,
    get_feature_flag_manager,
    is_feature_enabled,
)


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_manager(temp_config_dir):
    """Create a test feature flag manager."""
    config_path = temp_config_dir / "feature_flags.json"
    return FeatureFlagManager(config_path=config_path)


class TestFeatureFlag:
    """Tests for FeatureFlag model."""

    def test_feature_flag_creation(self):
        """Test creating a feature flag."""
        flag = FeatureFlag(
            name="test_feature",
            status=FeatureStatus.ENABLED,
            description="Test feature",
        )

        assert flag.name == "test_feature"
        assert flag.status == FeatureStatus.ENABLED
        assert flag.rollout_percentage == 100.0

    def test_feature_flag_with_dependencies(self):
        """Test feature flag with dependencies."""
        flag = FeatureFlag(
            name="advanced_feature",
            status=FeatureStatus.BETA,
            description="Advanced feature",
            dependencies=["base_feature"],
            rollout_percentage=50.0,
        )

        assert len(flag.dependencies) == 1
        assert flag.dependencies[0] == "base_feature"


class TestFeatureFlagManager:
    """Tests for FeatureFlagManager."""

    def test_manager_initialization(self, test_manager):
        """Test manager initializes with default config."""
        assert test_manager.config_path.exists()
        assert len(test_manager.flags) > 0

    def test_default_flags_created(self, test_manager):
        """Test default flags are created."""
        # Check some expected default flags
        assert "validation_layer" in test_manager.flags
        assert "rate_limiting" in test_manager.flags
        assert "mcp_integration" in test_manager.flags

    def test_is_enabled_for_enabled_feature(self, test_manager):
        """Test checking if enabled feature is enabled."""
        # validation_layer should be enabled by default
        assert test_manager.is_enabled("validation_layer") is True

    def test_is_enabled_for_disabled_feature(self, test_manager):
        """Test checking if disabled feature is disabled."""
        # rate_limiting should be disabled by default
        assert test_manager.is_enabled("rate_limiting") is False

    def test_is_enabled_for_unknown_feature(self, test_manager):
        """Test checking unknown feature returns False."""
        assert test_manager.is_enabled("unknown_feature") is False

    def test_environment_override(self, test_manager, monkeypatch):
        """Test environment variable overrides config."""
        # Set environment override
        monkeypatch.setenv("FEATURE_RATE_LIMITING", "true")

        # Should be enabled despite config saying disabled
        assert test_manager.is_enabled("rate_limiting") is True

    def test_environment_override_disabled(self, test_manager, monkeypatch):
        """Test environment can disable enabled feature."""
        # Set environment override
        monkeypatch.setenv("FEATURE_VALIDATION_LAYER", "false")

        # Should be disabled despite config saying enabled
        assert test_manager.is_enabled("validation_layer") is False

    def test_set_status(self, test_manager):
        """Test setting feature status."""
        test_manager.set_status("rate_limiting", FeatureStatus.ENABLED)

        flag = test_manager.flags["rate_limiting"]
        assert flag.status == FeatureStatus.ENABLED

    def test_set_status_unknown_feature(self, test_manager):
        """Test setting status of unknown feature raises error."""
        with pytest.raises(ValueError, match="Unknown feature flag"):
            test_manager.set_status("unknown_feature", FeatureStatus.ENABLED)

    def test_get_status(self, test_manager):
        """Test getting feature status."""
        status = test_manager.get_status("validation_layer")
        assert status == FeatureStatus.ENABLED

    def test_get_status_unknown(self, test_manager):
        """Test getting status of unknown feature."""
        status = test_manager.get_status("unknown_feature")
        assert status is None

    def test_is_beta(self, test_manager):
        """Test checking if feature is in beta."""
        # Set a feature to beta
        test_manager.flags["cognee_knowledge_graph"].status = FeatureStatus.BETA

        assert test_manager.is_beta("cognee_knowledge_graph") is True
        assert test_manager.is_beta("validation_layer") is False

    def test_save_and_reload(self, test_manager, temp_config_dir):
        """Test saving config and reloading."""
        # Modify a flag
        test_manager.set_status("rate_limiting", FeatureStatus.ENABLED)
        test_manager.save()

        # Create new manager with same config file
        new_manager = FeatureFlagManager(config_path=test_manager.config_path)

        # Should have the updated status
        assert new_manager.get_status("rate_limiting") == FeatureStatus.ENABLED

    def test_list_all(self, test_manager):
        """Test listing all flags."""
        all_flags = test_manager.list_all()

        assert isinstance(all_flags, dict)
        assert len(all_flags) > 0
        assert "validation_layer" in all_flags

    def test_rollout_percentage_testing(self, test_manager):
        """Test testing mode with rollout percentage."""
        # Set feature to testing with 0% rollout
        test_manager.flags["test_feature"] = FeatureFlag(
            name="test_feature",
            status=FeatureStatus.TESTING,
            description="Test",
            rollout_percentage=0.0,
        )

        # Should always be False with 0% rollout
        # Note: This is probabilistic, so we test multiple times
        results = [test_manager.is_enabled("test_feature") for _ in range(10)]
        assert all(result is False for result in results)


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_get_global_manager(self):
        """Test getting global manager instance."""
        manager1 = get_feature_flag_manager()
        manager2 = get_feature_flag_manager()

        # Should be same instance
        assert manager1 is manager2

    def test_is_feature_enabled_function(self):
        """Test convenience function for checking enabled."""
        # This uses the global manager
        result = is_feature_enabled("validation_layer")

        # Should be a boolean
        assert isinstance(result, bool)


class TestConfigFileFormat:
    """Tests for config file format."""

    def test_config_file_structure(self, test_manager):
        """Test config file has correct structure."""
        with open(test_manager.config_path) as f:
            data = json.load(f)

        assert "features" in data
        assert isinstance(data["features"], dict)

    def test_feature_entry_structure(self, test_manager):
        """Test individual feature entry structure."""
        with open(test_manager.config_path) as f:
            data = json.load(f)

        validation_layer = data["features"]["validation_layer"]

        assert "status" in validation_layer
        assert "description" in validation_layer
        assert "rollout_percentage" in validation_layer
