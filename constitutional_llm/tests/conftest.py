import os
import sys

import pytest

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.bee_implementations import SocialPosterBee, SponsorHunterBee
from src.constitutional_audit import ConstitutionalAuditEngine
from src.constitutional_gateway import ConstitutionalGateway


@pytest.fixture
def gateway():
    return ConstitutionalGateway()


@pytest.fixture
def audit_engine():
    log_file = "test_audit_log.jsonl"
    if os.path.exists(log_file):
        os.remove(log_file)
    engine = ConstitutionalAuditEngine(log_file=log_file)
    yield engine
    if os.path.exists(log_file):
        os.remove(log_file)


@pytest.fixture
def sponsor_bee():
    return SponsorHunterBee()


@pytest.fixture
def social_bee():
    return SocialPosterBee()
