"""
Payment and treasury schemas for financial operations.
"""

from decimal import Decimal
from enum import Enum

from pydantic import Field, field_validator

from hive.schemas.base import BaseSchema, TimestampedSchema


class PaymentStatus(str, Enum):
    """Status of a payment transaction."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentProvider(str, Enum):
    """Payment provider types."""

    STRIPE = "stripe"
    CRYPTO = "crypto"
    INTERNAL = "internal"


class PaymentMethodSchema(BaseSchema):
    """Schema for payment method details."""

    method_id: str = Field(..., description="Unique payment method identifier")
    provider: PaymentProvider
    type: str = Field(..., description="Payment method type (card, crypto, etc.)")
    last_four: str | None = Field(None, description="Last 4 digits for display")
    is_default: bool = Field(default=False, description="Default payment method")


class PaymentIntentSchema(TimestampedSchema):
    """Schema for payment intent tracking."""

    intent_id: str = Field(..., description="Unique payment intent identifier")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="usd", description="Currency code (ISO 4217)")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Current status")
    provider: PaymentProvider
    provider_intent_id: str | None = Field(None, description="Provider-specific intent ID")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Ensure currency is uppercase."""
        return v.upper()


class TransactionSchema(TimestampedSchema):
    """Schema for completed transactions."""

    transaction_id: str = Field(..., description="Unique transaction identifier")
    intent_id: str | None = Field(None, description="Related payment intent")
    from_wallet: str | None = Field(None, description="Source wallet address")
    to_wallet: str = Field(..., description="Destination wallet address")
    amount: Decimal = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="usd", description="Currency code")
    status: PaymentStatus
    provider: PaymentProvider
    tx_hash: str | None = Field(None, description="Blockchain transaction hash")
    fee: Decimal | None = Field(None, ge=0, description="Transaction fee")
    notes: str | None = Field(None, description="Transaction notes")


class WalletSchema(TimestampedSchema):
    """Schema for wallet information."""

    wallet_id: str = Field(..., description="Unique wallet identifier")
    address: str = Field(..., description="Wallet address")
    balance: Decimal = Field(default=Decimal("0"), ge=0, description="Current balance")
    currency: str = Field(default="usd", description="Currency code")
    is_hive_wallet: bool = Field(
        default=False, description="True if this is the hive's primary wallet"
    )
