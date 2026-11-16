"""
Generic repository pattern for structured data storage.

This module provides a base repository class that abstracts CRUD operations
for structured data, integrating with the existing StorageAdapter system.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar
from uuid import uuid4

from hive.utils.storage_adapter import StorageAdapter

T = TypeVar("T")


class RepositoryItem(Protocol):
    """Protocol for items that can be stored in a repository."""

    id: str


class Repository(Generic[T]):
    """
    Base repository class providing CRUD operations for structured data.

    This class provides a generic interface for storing and retrieving
    structured data using the honeycomb storage system. It supports both
    file-based and Firestore storage through the StorageAdapter.

    Attributes:
        collection_name: Name of the collection/file for this repository
        storage_adapter: Adapter for storage operations
        logger: Logger instance for this repository

    Example:
        >>> repo = Repository[dict]("my_collection", honeycomb_path)
        >>> item = {"id": "123", "name": "Test", "value": 42}
        >>> repo.create(item)
        >>> retrieved = repo.get("123")
        >>> repo.update("123", {"value": 100})
        >>> repo.delete("123")
    """

    def __init__(self, collection_name: str, base_path: Path | None = None):
        """
        Initialize a repository.

        Args:
            collection_name: Name of the collection (used as filename)
            base_path: Base path for storage (defaults to honeycomb/)
        """
        self.collection_name = collection_name
        self.filename = f"{collection_name}.json"

        # Default to honeycomb directory
        if base_path is None:
            base_path = Path(__file__).parent.parent / "honeycomb"

        self.storage_adapter = StorageAdapter(base_path)
        self.logger = logging.getLogger(f"Repository.{collection_name}")

    def _load_data(self) -> dict[str, Any]:
        """Load the entire collection from storage."""
        data = self.storage_adapter.read(self.filename)
        if not data:
            data = {
                "collection": self.collection_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "items": {},
            }
        return data

    def _save_data(self, data: dict[str, Any]) -> None:
        """Save the entire collection to storage."""
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.storage_adapter.write(self.filename, data)

    def create(self, item: dict[str, Any], item_id: str | None = None) -> str:
        """
        Create a new item in the repository.

        Args:
            item: The item data to store
            item_id: Optional ID for the item (generated if not provided)

        Returns:
            The ID of the created item

        Example:
            >>> repo.create({"name": "Test", "value": 42})
            'uuid-here'
            >>> repo.create({"name": "Test"}, item_id="custom-id")
            'custom-id'
        """
        data = self._load_data()

        if item_id is None:
            item_id = str(uuid4())

        if item_id in data["items"]:
            raise ValueError(f"Item with ID {item_id} already exists")

        item["id"] = item_id
        item["created_at"] = datetime.now(timezone.utc).isoformat()
        data["items"][item_id] = item

        self._save_data(data)
        self.logger.info(f"Created item {item_id} in {self.collection_name}")
        return item_id

    def get(self, item_id: str) -> dict[str, Any] | None:
        """
        Retrieve an item by ID.

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            The item data if found, None otherwise

        Example:
            >>> item = repo.get("123")
            >>> if item:
            ...     print(item["name"])
        """
        data = self._load_data()
        return data["items"].get(item_id)

    def list(
        self,
        filter_fn: Any | None = None,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """
        List items in the repository with optional filtering.

        Args:
            filter_fn: Optional function to filter items
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            List of items matching the criteria

        Example:
            >>> # Get all items
            >>> all_items = repo.list()
            >>> # Get items with value > 50
            >>> filtered = repo.list(filter_fn=lambda x: x.get("value", 0) > 50)
            >>> # Get first 10 items
            >>> page = repo.list(limit=10, offset=0)
        """
        data = self._load_data()
        items = list(data["items"].values())

        if filter_fn:
            items = [item for item in items if filter_fn(item)]

        if offset > 0:
            items = items[offset:]

        if limit is not None:
            items = items[:limit]

        return items

    def update(self, item_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing item.

        Args:
            item_id: The ID of the item to update
            updates: Dictionary of fields to update

        Returns:
            True if the item was updated, False if not found

        Example:
            >>> repo.update("123", {"value": 100, "status": "active"})
            True
        """
        data = self._load_data()

        if item_id not in data["items"]:
            self.logger.warning(f"Item {item_id} not found for update")
            return False

        item = data["items"][item_id]
        item.update(updates)
        item["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_data(data)
        self.logger.info(f"Updated item {item_id} in {self.collection_name}")
        return True

    def delete(self, item_id: str) -> bool:
        """
        Delete an item from the repository.

        Args:
            item_id: The ID of the item to delete

        Returns:
            True if the item was deleted, False if not found

        Example:
            >>> repo.delete("123")
            True
        """
        data = self._load_data()

        if item_id not in data["items"]:
            self.logger.warning(f"Item {item_id} not found for deletion")
            return False

        del data["items"][item_id]
        self._save_data(data)
        self.logger.info(f"Deleted item {item_id} from {self.collection_name}")
        return True

    def count(self) -> int:
        """
        Get the total number of items in the repository.

        Returns:
            The number of items

        Example:
            >>> total = repo.count()
            >>> print(f"Repository contains {total} items")
        """
        data = self._load_data()
        return len(data["items"])

    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists in the repository.

        Args:
            item_id: The ID to check

        Returns:
            True if the item exists, False otherwise

        Example:
            >>> if repo.exists("123"):
            ...     print("Item exists")
        """
        data = self._load_data()
        return item_id in data["items"]

    def clear(self) -> None:
        """
        Clear all items from the repository.

        Warning:
            This operation cannot be undone.

        Example:
            >>> repo.clear()  # Remove all items
        """
        data = {
            "collection": self.collection_name,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "items": {},
        }
        self._save_data(data)
        self.logger.warning(f"Cleared all items from {self.collection_name}")


class HoneycombRepository:
    """
    Factory class for creating repositories in the honeycomb.

    This class provides a convenient way to access commonly used repositories
    with the correct paths already configured.

    Example:
        >>> repos = HoneycombRepository()
        >>> user_repo = repos.get_repository("users")
        >>> user_repo.create({"username": "alice", "role": "admin"})
    """

    def __init__(self, honeycomb_path: Path | None = None):
        """
        Initialize the repository factory.

        Args:
            honeycomb_path: Path to the honeycomb directory
        """
        if honeycomb_path is None:
            honeycomb_path = Path(__file__).parent.parent / "honeycomb"
        self.honeycomb_path = honeycomb_path
        self._repositories: dict[str, Repository[Any]] = {}

    def get_repository(self, collection_name: str) -> Repository[Any]:
        """
        Get or create a repository for a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Repository instance for the collection

        Example:
            >>> repos = HoneycombRepository()
            >>> users = repos.get_repository("users")
            >>> events = repos.get_repository("events")
        """
        if collection_name not in self._repositories:
            self._repositories[collection_name] = Repository(collection_name, self.honeycomb_path)
        return self._repositories[collection_name]
