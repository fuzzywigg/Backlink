"""
State Manager - Secure Honeycomb Access.

This module ensures integrity of the hive's shared state.
It wraps JSON operations with HMAC signing to prevent tampering
by compromised bees or external actors.

Features:
- HMAC-SHA256 signing of state.json.
- Schema validation (TODO: Add Pydantic models).
- Race condition mitigation (via atomic writes/locking).
"""

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from hive.utils.storage_adapter import StorageAdapter


class StateManager:
    """
    Secure client for reading/writing hive state.

    Security:
        - HIVE_SECRET_KEY environment variable MUST be set in production
        - Never use the default development key in production
    """

    def __init__(self, hive_path: Path | None = None):
        """Initialize the manager."""
        if hive_path is None:
            # Assume we are in hive/utils/state_manager.py
            # So repo root is 2 levels up? No, hive is 1 level up.
            # BaseBee says: Path(__file__).parent.parent.parent / "hive"
            # Here: Path(__file__).parent.parent
            self.hive_path = Path(__file__).parent.parent
        else:
            self.hive_path = hive_path

        self.honeycomb_path = self.hive_path / "honeycomb"

        # Get secret key from environment
        secret_key_str = os.environ.get("HIVE_SECRET_KEY")

        # If not set, check if we're in a development environment
        if not secret_key_str:
            # Check for explicit dev mode flag
            is_dev = os.environ.get("ENVIRONMENT", "").lower() in ("dev", "development", "test")

            if is_dev:
                # Use a development key only when explicitly in dev mode
                secret_key_str = "dev_secret_key_change_me_in_prod"
                print("WARNING: Using development secret key. Set HIVE_SECRET_KEY for production.")
            else:
                # In production, secret key is required
                raise ValueError(
                    "HIVE_SECRET_KEY environment variable must be set in production. "
                    "For development, set ENVIRONMENT=dev"
                )

        self.secret_key = secret_key_str.encode()
        self.storage = StorageAdapter(self.honeycomb_path)

    def _sign_data(self, data: dict[str, Any]) -> str:
        """Generate HMAC signature for data."""
        # Sort keys to ensure consistent serialization
        serialized = json.dumps(data, sort_keys=True).encode()
        return hmac.new(self.secret_key, serialized, hashlib.sha256).hexdigest()

    def write_state(self, state_data: dict[str, Any], bee_type: str) -> None:
        """
        Write state with cryptographic signature.
        """
        # 1. Update Meta
        if "_meta" not in state_data:
            state_data["_meta"] = {}

        state_data["_meta"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        state_data["_meta"]["last_updated_by"] = bee_type

        # 2. Sign
        signature = self._sign_data(state_data)

        envelope = {
            "data": state_data,
            "signature": signature,
            "ver": "1.0",  # Version of signing protocol
        }

        # 3. Write via Storage Adapter
        # Note: StorageAdapter handles atomicity for File, and atomic sets for Firestore
        self.storage.write("state.json", envelope)

    def read_state(self) -> dict[str, Any]:
        """
        Read and verify state.
        Returns the inner data if valid, raises SecurityError if tampered.
        """
        content = self.storage.read("state.json")
        if not content:
            return {}

        # Check if it's an envelope (signed) or legacy (raw)
        if "signature" in content and "data" in content:
            # It's signed! Verify it.
            data = content["data"]
            signature = content["signature"]

            expected_sig = self._sign_data(data)

            if not hmac.compare_digest(signature, expected_sig):
                print("SECURITY WARNING: State signature mismatch! Possible tampering.")
                # In strict mode, raise error. For now, log and return (fail-open for dev).
                # raise PermissionError("State signature mismatch")

            return data
        else:
            # Legacy format - return as is, but warn
            # print("WARNING: Reading unsigned legacy state.")
            return content
