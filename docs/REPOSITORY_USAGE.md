# Repository Pattern Usage Guide

## Overview

The `repository.py` module provides a generic repository pattern for structured data storage in the Backlink Broadcast Hive. It abstracts CRUD (Create, Read, Update, Delete) operations and integrates seamlessly with the existing StorageAdapter system, supporting both file-based and Firestore storage.

## Why a Repository?

The repository pattern provides:

- **Abstraction**: Clean separation between business logic and data storage
- **Type Safety**: Generic type support for structured data
- **Consistency**: Standardized way to handle data across the hive
- **Flexibility**: Works with both local files and Firestore
- **Stigmergy**: Fits naturally into the bee communication pattern

## Basic Usage

### Creating a Repository

```python
from pathlib import Path
from hive.utils.repository import Repository

# Create a repository for storing user data
users_repo = Repository("users")

# Or specify a custom path
custom_repo = Repository("my_collection", base_path=Path("/custom/path"))
```

### CRUD Operations

#### Create

```python
# Create with auto-generated ID
user_data = {"username": "alice", "role": "admin", "email": "alice@backlink.fm"}
user_id = users_repo.create(user_data)
print(f"Created user: {user_id}")

# Create with custom ID
users_repo.create({"username": "bob"}, item_id="bob-123")
```

#### Read

```python
# Get a single item
user = users_repo.get(user_id)
if user:
    print(f"Username: {user['username']}")

# Check if item exists
if users_repo.exists(user_id):
    print("User found!")

# Get total count
total_users = users_repo.count()
print(f"Total users: {total_users}")
```

#### Update

```python
# Update fields
success = users_repo.update(
    user_id, {"email": "alice@newdomain.com", "last_login": "2026-02-07T10:00:00Z"}
)

if success:
    print("User updated!")
```

#### Delete

```python
# Delete an item
success = users_repo.delete(user_id)
if success:
    print("User deleted!")
```

### Listing and Filtering

```python
# Get all items
all_users = users_repo.list()

# Filter items
admins = users_repo.list(filter_fn=lambda u: u.get("role") == "admin")

# Pagination
page_1 = users_repo.list(limit=10, offset=0)
page_2 = users_repo.list(limit=10, offset=10)
```

### Clear Repository

```python
# Remove all items (use with caution!)
users_repo.clear()
```

## Using the Factory

For convenience, use `HoneycombRepository` to manage multiple repositories:

```python
from hive.utils.repository import HoneycombRepository

# Create factory
repos = HoneycombRepository()

# Get repositories
users = repos.get_repository("users")
events = repos.get_repository("events")
sessions = repos.get_repository("sessions")

# The factory ensures same instances are reused
users_again = repos.get_repository("users")
assert users is users_again  # True
```

## Example: Bee Using Repository

Here's how a bee might use the repository pattern:

```python
from hive.bees.base_bee import ScoutBee
from hive.utils.repository import Repository
from typing import Any


class ListenerTrackerBee(ScoutBee):
    """Bee that tracks listener activity using repository pattern."""

    BEE_TYPE = "listener_tracker"
    BEE_NAME = "Listener Tracker"
    CATEGORY = "community"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.listeners_repo = Repository("listeners")

    def work(self, task: dict[str, Any] | None = None) -> dict[str, Any]:
        """Track and manage listener data."""
        # Record a new listener
        listener_id = self.listeners_repo.create(
            {"username": "node_42", "first_seen": "2026-02-07T10:00:00Z", "interactions": 0}
        )

        # Update interaction count
        listener = self.listeners_repo.get(listener_id)
        if listener:
            self.listeners_repo.update(
                listener_id,
                {"interactions": listener["interactions"] + 1, "last_seen": "2026-02-07T11:00:00Z"},
            )

        # Get active listeners
        active = self.listeners_repo.list(filter_fn=lambda l: l.get("interactions", 0) > 5)

        return {
            "status": "success",
            "tracked_listeners": self.listeners_repo.count(),
            "active_listeners": len(active),
        }
```

## Storage Format

Data is stored in JSON format:

```json
{
  "collection": "users",
  "created_at": "2026-02-07T10:00:00.000000",
  "updated_at": "2026-02-07T11:30:00.000000",
  "items": {
    "uuid-here": {
      "id": "uuid-here",
      "username": "alice",
      "role": "admin",
      "created_at": "2026-02-07T10:00:00.000000",
      "updated_at": "2026-02-07T11:30:00.000000"
    }
  }
}
```

## Integration with Firestore

The repository automatically uses Firestore when the environment is configured:

```bash
export STORAGE_TYPE=FIRESTORE
export GCP_PROJECT_ID=your-project-id
```

No code changes needed - the repository adapts automatically!

## Best Practices

1. **One Repository Per Entity Type**: Create separate repositories for different data types
   ```python
   users_repo = Repository("users")
   events_repo = Repository("events")
   ```

2. **Use Descriptive Collection Names**: Make it clear what the repository contains
   ```python
   Repository("listener_sessions")  # Good
   Repository("data")  # Bad - too generic
   ```

3. **Handle None Returns**: Always check if items exist
   ```python
   item = repo.get(item_id)
   if item is not None:
       # Use item
   ```

4. **Use Filters for Complex Queries**: Leverage the filter function
   ```python
   recent = repo.list(filter_fn=lambda x: x["timestamp"] > cutoff_time)
   ```

5. **Avoid Excessive Clear Operations**: Clearing removes all data permanently

## Common Patterns

### Caching Pattern

```python
class CachingBee(ScoutBee):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = Repository("bee_cache")

    def get_or_fetch(self, key: str):
        # Check cache first
        cached = self.cache.get(key)
        if cached:
            return cached["value"]

        # Fetch and cache
        value = self.expensive_operation(key)
        self.cache.create({"value": value}, item_id=key)
        return value
```

### Event Logging Pattern

```python
from hive.utils.repository import Repository
from datetime import datetime, timezone

events_repo = Repository("events")


def log_event(event_type: str, data: dict):
    events_repo.create(
        {"type": event_type, "timestamp": datetime.now(timezone.utc).isoformat(), "data": data}
    )


# Usage
log_event("song_played", {"title": "Track", "artist": "Artist"})
log_event("listener_joined", {"username": "alice"})
```

### Registry Pattern

```python
class BeeRegistry:
    def __init__(self):
        self.registry = Repository("bee_registry")

    def register_bee(self, bee_type: str, config: dict):
        self.registry.create(config, item_id=bee_type)

    def get_bee_config(self, bee_type: str):
        return self.registry.get(bee_type)

    def list_active_bees(self):
        return self.registry.list(filter_fn=lambda b: b.get("active", False))
```

## Migration from Direct File Access

If you're currently using direct file access, migrating is straightforward:

**Before:**
```python
import json

with open("data.json") as f:
    data = json.load(f)

items = data.get("items", {})
```

**After:**
```python
from hive.utils.repository import Repository

repo = Repository("data")
items = repo.list()
```

## Testing

The repository module includes comprehensive tests. Run them with:

```bash
pytest hive/tests/test_repository.py -v
```

## Summary

The repository pattern provides a clean, consistent way to manage structured data in the Backlink Broadcast Hive. It integrates with existing infrastructure, supports both local and cloud storage, and follows the stigmergy communication pattern used throughout the swarm.
