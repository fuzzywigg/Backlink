"""
Tests for Pydantic schemas.
"""

import json
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from hive.schemas import (
    BeeCategory,
    BeeConfig,
    BeeRole,
    BeeStatus,
    BeeWorkResult,
    HealthCheckResponse,
    HoneycombStateSchema,
    IntelSchema,
    PaymentIntentSchema,
    PaymentProvider,
    PaymentStatus,
    TaskPriority,
    TaskSchema,
    TaskStatus,
    TransactionSchema,
    WisdomEntrySchema,
    WisdomSchema,
)


class TestHoneycombSchemas:
    """Tests for honeycomb-related schemas."""

    def test_task_schema_valid(self):
        """Test valid task creation."""
        task = TaskSchema(
            task_id="task_123",
            bee_type="trend_scout",
            priority=TaskPriority.HIGH,
            payload={"query": "trending music"},
        )

        assert task.task_id == "task_123"
        assert task.bee_type == "trend_scout"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.PENDING
        assert task.payload == {"query": "trending music"}

    def test_task_schema_invalid_empty_id(self):
        """Test that empty task_id is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            TaskSchema(
                task_id="   ",  # Whitespace only
                bee_type="trend_scout",
            )

        assert "task_id" in str(exc_info.value)

    def test_task_schema_timestamps(self):
        """Test automatic timestamp creation."""
        task = TaskSchema(task_id="task_123", bee_type="test")

        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)

    def test_intel_schema_valid(self):
        """Test valid intel creation."""
        intel = IntelSchema(
            intel_id="intel_456",
            source="trend_scout",
            category="music_trends",
            data={"trending": ["track1", "track2"]},
            confidence=0.85,
            tags=["music", "trends"],
        )

        assert intel.intel_id == "intel_456"
        assert intel.confidence == 0.85
        assert len(intel.tags) == 2

    def test_intel_schema_confidence_validation(self):
        """Test confidence score validation (0-1)."""
        # Valid
        intel = IntelSchema(
            intel_id="intel_1",
            source="scout",
            category="test",
            data={},
            confidence=0.5,
        )
        assert intel.confidence == 0.5

        # Invalid - too high
        with pytest.raises(ValidationError):
            IntelSchema(
                intel_id="intel_2",
                source="scout",
                category="test",
                data={},
                confidence=1.5,
            )

    def test_wisdom_schema(self):
        """Test wisdom schema with entries."""
        entry1 = WisdomEntrySchema(
            entry_id="wisdom_1",
            category="music_taste",
            content={"preference": "electronic"},
            learned_from=["listener_intel"],
        )

        wisdom = WisdomSchema(entries=[entry1])

        assert len(wisdom.entries) == 1
        assert wisdom.entries[0].entry_id == "wisdom_1"

    def test_honeycomb_state_schema(self):
        """Test main state schema."""
        state = HoneycombStateSchema(
            current_track={"title": "Test Track", "artist": "Test Artist"},
            queue=[{"title": "Next Track"}],
            listeners={"count": 42},
        )

        assert state.current_track["title"] == "Test Track"
        assert len(state.queue) == 1
        assert state.listeners["count"] == 42


class TestPaymentSchemas:
    """Tests for payment-related schemas."""

    def test_payment_intent_schema(self):
        """Test payment intent creation."""
        intent = PaymentIntentSchema(
            intent_id="pi_123",
            amount=Decimal("10.50"),
            currency="usd",
            provider=PaymentProvider.STRIPE,
        )

        assert intent.intent_id == "pi_123"
        assert intent.amount == Decimal("10.50")
        assert intent.currency == "USD"  # Should be uppercase
        assert intent.status == PaymentStatus.PENDING

    def test_payment_intent_currency_uppercase(self):
        """Test that currency is converted to uppercase."""
        intent = PaymentIntentSchema(
            intent_id="pi_123",
            amount=Decimal("10.00"),
            currency="eur",
            provider=PaymentProvider.STRIPE,
        )

        assert intent.currency == "EUR"

    def test_payment_intent_invalid_amount(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(ValidationError):
            PaymentIntentSchema(
                intent_id="pi_123",
                amount=Decimal("-10.00"),
                currency="usd",
                provider=PaymentProvider.STRIPE,
            )

    def test_transaction_schema(self):
        """Test transaction schema."""
        tx = TransactionSchema(
            transaction_id="tx_123",
            to_wallet="0x1234",
            amount=Decimal("50.00"),
            currency="usd",
            status=PaymentStatus.SUCCEEDED,
            provider=PaymentProvider.CRYPTO,
        )

        assert tx.transaction_id == "tx_123"
        assert tx.to_wallet == "0x1234"
        assert tx.amount == Decimal("50.00")


class TestBeeSchemas:
    """Tests for bee-related schemas."""

    def test_bee_config_schema(self):
        """Test bee configuration."""
        config = BeeConfig(
            bee_type="trend_scout",
            bee_name="Trend Scout",
            category=BeeCategory.RESEARCH,
            role=BeeRole.SCOUT,
            enabled=True,
        )

        assert config.bee_type == "trend_scout"
        assert config.category == BeeCategory.RESEARCH
        assert config.role == BeeRole.SCOUT

    def test_bee_work_result_schema(self):
        """Test bee work result."""
        result = BeeWorkResult(
            bee_type="trend_scout",
            status=BeeStatus.COMPLETED,
            success=True,
            data={"trends": ["track1", "track2"]},
            intel_generated=["intel_1", "intel_2"],
            execution_time_ms=150.5,
        )

        assert result.bee_type == "trend_scout"
        assert result.success is True
        assert len(result.intel_generated) == 2
        assert result.execution_time_ms == 150.5

    def test_bee_work_result_with_error(self):
        """Test bee work result with error."""
        result = BeeWorkResult(
            bee_type="trend_scout",
            status=BeeStatus.FAILED,
            success=False,
            error="API timeout",
        )

        assert result.success is False
        assert result.error == "API timeout"
        assert result.status == BeeStatus.FAILED


class TestSchemaSerialization:
    """Test schema serialization and JSON compatibility."""

    def test_task_to_dict(self):
        """Test converting task to dict."""
        task = TaskSchema(
            task_id="task_123",
            bee_type="test",
            payload={"key": "value"},
        )

        data = task.model_dump()

        assert isinstance(data, dict)
        assert data["task_id"] == "task_123"
        assert data["bee_type"] == "test"

    def test_task_to_json(self):
        """Test converting task to JSON."""
        task = TaskSchema(
            task_id="task_123",
            bee_type="test",
        )

        json_str = task.model_dump_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["task_id"] == "task_123"

    def test_task_from_dict(self):
        """Test creating task from dict."""
        data = {
            "task_id": "task_123",
            "bee_type": "test",
            "priority": "high",
            "status": "pending",
        }

        task = TaskSchema(**data)

        assert task.task_id == "task_123"
        assert task.priority == TaskPriority.HIGH


class TestSchemaExtraFields:
    """Test handling of extra fields."""

    def test_state_allows_extra_fields(self):
        """Test that HoneycombStateSchema allows extra fields."""
        state = HoneycombStateSchema(
            current_track={"title": "Test"},
            custom_field="custom_value",  # Extra field
        )

        # Should not raise error
        assert state.current_track["title"] == "Test"

    def test_task_forbids_extra_fields(self):
        """Test that TaskSchema forbids extra fields."""
        with pytest.raises(ValidationError):
            TaskSchema(
                task_id="task_123",
                bee_type="test",
                unknown_field="value",  # Extra field - should fail
            )


class TestHealthCheckResponse:
    """Tests for /health response schema (including build provenance)."""

    def test_health_check_required_fields(self):
        """Legacy clients still receive status/version/uptime/hive_status."""
        response = HealthCheckResponse(
            status="healthy",
            version="1.1.0",
            uptime_seconds=12.5,
            hive_status={"queen_active": True},
        )

        assert response.status == "healthy"
        assert response.version == "1.1.0"
        assert response.uptime_seconds == 12.5
        assert response.hive_status["queen_active"] is True

    def test_health_check_provenance_defaults(self):
        """Unset provenance must not invent a fake SHA."""
        response = HealthCheckResponse(
            status="healthy",
            version="1.1.0",
            uptime_seconds=0.0,
        )

        assert response.git_sha == "unknown"
        assert response.build_id is None
        assert response.build_time is None

    def test_health_check_provenance_fields(self):
        """Provenance fields are accepted when provided."""
        response = HealthCheckResponse(
            status="healthy",
            version="1.1.0",
            uptime_seconds=1.0,
            git_sha="abc1234",
            build_id="build-99",
            build_time="20260322_1200",
        )

        data = response.model_dump()
        assert data["git_sha"] == "abc1234"
        assert data["build_id"] == "build-99"
        assert data["build_time"] == "20260322_1200"
        assert data["status"] == "healthy"

    def test_health_check_rejects_negative_uptime(self):
        """Uptime must be non-negative."""
        with pytest.raises(ValidationError):
            HealthCheckResponse(
                status="healthy",
                version="1.1.0",
                uptime_seconds=-1.0,
            )
