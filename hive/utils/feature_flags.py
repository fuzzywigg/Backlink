"""
Feature flag system for controlled rollout of new features.

This module provides a centralized way to enable/disable features
and perform A/B testing without code deployments.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class FeatureStatus(str, Enum):
    """Status of a feature flag."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    TESTING = "testing"  # A/B test mode
    BETA = "beta"  # Beta testing


class FeatureFlag(BaseModel):
    """Configuration for a single feature flag."""

    name: str = Field(..., description="Unique feature name")
    status: FeatureStatus = Field(default=FeatureStatus.DISABLED)
    description: str = Field(..., description="What this feature does")
    rollout_percentage: float = Field(
        default=100.0, ge=0.0, le=100.0, description="Percentage of users to enable for"
    )
    dependencies: list[str] = Field(
        default_factory=list, description="Required features that must be enabled"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class FeatureFlagManager:
    """
    Manages feature flags for the hive.

    Usage:
        manager = FeatureFlagManager()
        if manager.is_enabled("new_payment_flow"):
            # Use new code
        else:
            # Use old code
    """

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the feature flag manager."""
        if config_path is None:
            # Default to hive/config/feature_flags.json
            config_path = Path(__file__).parent.parent / "config" / "feature_flags.json"

        self.config_path = config_path
        self.flags: dict[str, FeatureFlag] = {}
        self._load_flags()

    def _load_flags(self) -> None:
        """Load feature flags from configuration file."""
        if not self.config_path.exists():
            # Create default config
            self._create_default_config()

        try:
            with open(self.config_path) as f:
                data = json.load(f)
                for name, config in data.get("features", {}).items():
                    self.flags[name] = FeatureFlag(name=name, **config)
        except Exception as e:
            print(f"Warning: Failed to load feature flags: {e}")
            self.flags = {}

    def _create_default_config(self) -> None:
        """Create default feature flags configuration."""
        default_flags = {
            "features": {
                "validation_layer": {
                    "status": "enabled",
                    "description": "Pydantic validation for all data",
                    "rollout_percentage": 100.0,
                },
                "rate_limiting": {
                    "status": "disabled",
                    "description": "API rate limiting",
                    "rollout_percentage": 0.0,
                },
                "mcp_integration": {
                    "status": "disabled",
                    "description": "Model Context Protocol integration",
                    "rollout_percentage": 0.0,
                },
                "stripe_webhooks": {
                    "status": "enabled",
                    "description": "Stripe payment webhook handling",
                    "rollout_percentage": 100.0,
                },
                "cognee_knowledge_graph": {
                    "status": "testing",
                    "description": "Cognee-based knowledge graph",
                    "rollout_percentage": 50.0,
                },
                "constitutional_gateway": {
                    "status": "enabled",
                    "description": "Constitutional LLM governance",
                    "rollout_percentage": 100.0,
                },
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w") as f:
            json.dump(default_flags, f, indent=2)

    def is_enabled(self, feature_name: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature_name: Name of the feature to check

        Returns:
            True if feature is enabled, False otherwise
        """
        # Check environment override first
        env_override = os.environ.get(f"FEATURE_{feature_name.upper()}")
        if env_override is not None:
            return env_override.lower() in ("1", "true", "yes", "enabled")

        flag = self.flags.get(feature_name)
        if not flag:
            # Default to disabled for unknown features
            return False

        # Check status
        if flag.status == FeatureStatus.DISABLED:
            return False
        elif flag.status == FeatureStatus.ENABLED:
            return True
        elif flag.status in (FeatureStatus.TESTING, FeatureStatus.BETA):
            # For now, use rollout percentage as simple toggle
            # In production, this would use consistent hashing on user ID
            import random

            return random.random() * 100 < flag.rollout_percentage

        return False

    def is_beta(self, feature_name: str) -> bool:
        """Check if a feature is in beta testing."""
        flag = self.flags.get(feature_name)
        return flag is not None and flag.status == FeatureStatus.BETA

    def get_status(self, feature_name: str) -> FeatureStatus | None:
        """Get the status of a feature flag."""
        flag = self.flags.get(feature_name)
        return flag.status if flag else None

    def set_status(self, feature_name: str, status: FeatureStatus) -> None:
        """
        Set the status of a feature flag.

        Note: This updates in-memory only. Use save() to persist.
        """
        if feature_name not in self.flags:
            raise ValueError(f"Unknown feature flag: {feature_name}")

        self.flags[feature_name].status = status

    def save(self) -> None:
        """Save current flag configuration to disk."""
        data = {
            "features": {
                name: flag.model_dump(exclude={"name"})
                for name, flag in self.flags.items()
            }
        }

        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def list_all(self) -> dict[str, FeatureFlag]:
        """Get all feature flags."""
        return self.flags.copy()


# Global instance for easy access
_global_manager: FeatureFlagManager | None = None


def get_feature_flag_manager() -> FeatureFlagManager:
    """Get the global feature flag manager instance."""
    global _global_manager
    if _global_manager is None:
        _global_manager = FeatureFlagManager()
    return _global_manager


def is_feature_enabled(feature_name: str) -> bool:
    """Convenience function to check if a feature is enabled."""
    return get_feature_flag_manager().is_enabled(feature_name)
