"""
Non-secret build / source provenance for observability.

Values are expected to be injected at image build or deploy time via
environment variables. Never invent commit SHAs when unset.
"""

from __future__ import annotations

import os

# Preferred order for git/source identifiers set by CI or docker build.
_GIT_SHA_ENV_VARS: tuple[str, ...] = (
    "GIT_SHA",
    "SOURCE_COMMIT",
    "COMMIT_SHA",
)

_UNKNOWN = "unknown"


def _first_nonempty_env(*names: str) -> str | None:
    """Return the first non-empty trimmed env value, or None."""
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def resolve_git_sha() -> str:
    """
    Resolve git/source SHA from common CI / Cloud Build env vars.

    Returns:
        The commit SHA when set, otherwise ``\"unknown\"`` (never a fabricated hash).
    """
    return _first_nonempty_env(*_GIT_SHA_ENV_VARS) or _UNKNOWN


def resolve_build_id() -> str | None:
    """
    Resolve optional CI build identifier.

    Returns:
        Build ID string when ``BUILD_ID`` is set, otherwise ``None``.
    """
    return _first_nonempty_env("BUILD_ID")


def resolve_build_time() -> str | None:
    """
    Resolve optional build timestamp (non-secret).

    Checks ``BUILD_TIME`` then ``BUILD_TIMESTAMP`` (already used in Dockerfile).

    Returns:
        Timestamp string when set, otherwise ``None``.
    """
    return _first_nonempty_env("BUILD_TIME", "BUILD_TIMESTAMP")
