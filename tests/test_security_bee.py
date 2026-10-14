import os

import pytest

from hive.bees.base_bee import BaseBee


class _ProbeBee(BaseBee):
    """Minimal bee used only to exercise path guards (not collected as a test)."""

    def work(self, task=None):
        pass


@pytest.fixture
def temp_hive(tmp_path):
    """Create a temporary hive matching BaseBee's root/hive/honeycomb layout."""
    hive_path = tmp_path / "hive"
    honeycomb_path = hive_path / "hive" / "honeycomb"
    os.makedirs(honeycomb_path, exist_ok=True)
    return hive_path


def test_path_traversal_read(temp_hive):
    """Test that reading outside honeycomb is blocked."""
    bee = _ProbeBee(hive_path=str(temp_hive))

    # Create a secret file outside honeycomb
    secret_file = temp_hive / "secret.txt"
    with open(secret_file, "w") as f:
        f.write('{"secret": "exposed"}')

    # Attempt to read it using traversal — StorageAdapter raises on traversal
    with pytest.raises(ValueError, match="Path traversal detected"):
        bee._read_json("../secret.txt")


def test_path_traversal_write(temp_hive):
    """Test that writing outside honeycomb is blocked."""
    bee = _ProbeBee(hive_path=str(temp_hive))

    # Attempt to write outside honeycomb — StorageAdapter raises on traversal
    with pytest.raises(ValueError, match="Path traversal detected"):
        bee._write_json("../hacked.json", {"hacked": True})

    # Check that file was NOT created
    hacked_file = temp_hive / "hacked.json"
    assert not hacked_file.exists()


def test_valid_read_write(temp_hive):
    """Test that valid read/write still works."""
    bee = _ProbeBee(hive_path=str(temp_hive))

    # Write valid file
    bee._write_json("test.json", {"valid": True})

    # Check existence at BaseBee honeycomb path (root/hive/honeycomb)
    assert (temp_hive / "hive" / "honeycomb" / "test.json").exists()

    # Read back
    data = bee._read_json("test.json")
    assert data == {"valid": True}
