"""Tests for the repository module."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from hive.utils.repository import HoneycombRepository, Repository


@pytest.fixture
def temp_repo_path():
    """Create a temporary directory for repository testing."""
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def repository(temp_repo_path):
    """Create a test repository."""
    return Repository("test_collection", temp_repo_path)


class TestRepository:
    """Test suite for Repository class."""

    def test_create_item(self, repository):
        """Test creating a new item."""
        item = {"name": "Test Item", "value": 42}
        item_id = repository.create(item)

        assert item_id is not None
        assert len(item_id) > 0

        # Verify item can be retrieved
        retrieved = repository.get(item_id)
        assert retrieved is not None
        assert retrieved["name"] == "Test Item"
        assert retrieved["value"] == 42
        assert retrieved["id"] == item_id
        assert "created_at" in retrieved

    def test_create_item_with_custom_id(self, repository):
        """Test creating an item with a custom ID."""
        item = {"name": "Custom ID Item"}
        item_id = repository.create(item, item_id="custom-123")

        assert item_id == "custom-123"
        retrieved = repository.get("custom-123")
        assert retrieved is not None
        assert retrieved["name"] == "Custom ID Item"

    def test_create_duplicate_id_raises_error(self, repository):
        """Test that creating an item with duplicate ID raises error."""
        item = {"name": "First"}
        repository.create(item, item_id="dup-id")

        with pytest.raises(ValueError, match="already exists"):
            repository.create({"name": "Second"}, item_id="dup-id")

    def test_get_nonexistent_item(self, repository):
        """Test getting an item that doesn't exist."""
        result = repository.get("nonexistent-id")
        assert result is None

    def test_list_items(self, repository):
        """Test listing all items."""
        # Create multiple items
        repository.create({"name": "Item 1", "value": 10})
        repository.create({"name": "Item 2", "value": 20})
        repository.create({"name": "Item 3", "value": 30})

        items = repository.list()
        assert len(items) == 3
        assert all("name" in item for item in items)

    def test_list_with_filter(self, repository):
        """Test listing items with a filter function."""
        repository.create({"name": "Low", "value": 10})
        repository.create({"name": "High", "value": 100})
        repository.create({"name": "Medium", "value": 50})

        # Filter for items with value > 40
        filtered = repository.list(filter_fn=lambda x: x["value"] > 40)
        assert len(filtered) == 2
        assert all(item["value"] > 40 for item in filtered)

    def test_list_with_pagination(self, repository):
        """Test listing items with limit and offset."""
        for i in range(10):
            repository.create({"name": f"Item {i}", "index": i})

        # Get first 5 items
        page1 = repository.list(limit=5, offset=0)
        assert len(page1) == 5

        # Get next 5 items
        page2 = repository.list(limit=5, offset=5)
        assert len(page2) == 5

        # Verify different items
        page1_ids = {item["id"] for item in page1}
        page2_ids = {item["id"] for item in page2}
        assert page1_ids.isdisjoint(page2_ids)

    def test_update_item(self, repository):
        """Test updating an existing item."""
        item = {"name": "Original", "value": 42}
        item_id = repository.create(item)

        # Update the item
        success = repository.update(item_id, {"name": "Updated", "value": 100})
        assert success is True

        # Verify updates
        updated = repository.get(item_id)
        assert updated["name"] == "Updated"
        assert updated["value"] == 100
        assert "updated_at" in updated

    def test_update_nonexistent_item(self, repository):
        """Test updating an item that doesn't exist."""
        success = repository.update("nonexistent", {"name": "Test"})
        assert success is False

    def test_delete_item(self, repository):
        """Test deleting an item."""
        item = {"name": "To Delete"}
        item_id = repository.create(item)

        # Verify item exists
        assert repository.get(item_id) is not None

        # Delete the item
        success = repository.delete(item_id)
        assert success is True

        # Verify item is gone
        assert repository.get(item_id) is None

    def test_delete_nonexistent_item(self, repository):
        """Test deleting an item that doesn't exist."""
        success = repository.delete("nonexistent")
        assert success is False

    def test_count(self, repository):
        """Test counting items in repository."""
        assert repository.count() == 0

        repository.create({"name": "Item 1"})
        assert repository.count() == 1

        repository.create({"name": "Item 2"})
        repository.create({"name": "Item 3"})
        assert repository.count() == 3

    def test_exists(self, repository):
        """Test checking if an item exists."""
        item = {"name": "Test"}
        item_id = repository.create(item)

        assert repository.exists(item_id) is True
        assert repository.exists("nonexistent") is False

    def test_clear(self, repository):
        """Test clearing all items from repository."""
        # Create several items
        for i in range(5):
            repository.create({"name": f"Item {i}"})

        assert repository.count() == 5

        # Clear the repository
        repository.clear()
        assert repository.count() == 0
        assert len(repository.list()) == 0

    def test_persistence(self, temp_repo_path):
        """Test that data persists across repository instances."""
        # Create repository and add item
        repo1 = Repository("persistent", temp_repo_path)
        item_id = repo1.create({"name": "Persistent Item"})

        # Create new repository instance
        repo2 = Repository("persistent", temp_repo_path)
        retrieved = repo2.get(item_id)

        assert retrieved is not None
        assert retrieved["name"] == "Persistent Item"

    def test_storage_file_structure(self, temp_repo_path, repository):
        """Test that the storage file has correct structure."""
        repository.create({"name": "Test"})

        # Read the file directly
        file_path = temp_repo_path / "test_collection.json"
        assert file_path.exists()

        with open(file_path) as f:
            data = json.load(f)

        assert "collection" in data
        assert data["collection"] == "test_collection"
        assert "items" in data
        assert "created_at" in data
        assert len(data["items"]) == 1


class TestHoneycombRepository:
    """Test suite for HoneycombRepository factory class."""

    def test_get_repository(self, temp_repo_path):
        """Test getting a repository from the factory."""
        factory = HoneycombRepository(temp_repo_path)
        repo = factory.get_repository("test")

        assert repo is not None
        assert repo.collection_name == "test"

    def test_repository_reuse(self, temp_repo_path):
        """Test that the same repository instance is returned."""
        factory = HoneycombRepository(temp_repo_path)
        repo1 = factory.get_repository("test")
        repo2 = factory.get_repository("test")

        assert repo1 is repo2

    def test_multiple_repositories(self, temp_repo_path):
        """Test creating multiple different repositories."""
        factory = HoneycombRepository(temp_repo_path)
        users_repo = factory.get_repository("users")
        events_repo = factory.get_repository("events")

        # Create items in different repositories
        user_id = users_repo.create({"username": "alice"})
        event_id = events_repo.create({"type": "login"})

        assert users_repo.exists(user_id)
        assert events_repo.exists(event_id)
        assert not users_repo.exists(event_id)
        assert not events_repo.exists(user_id)
