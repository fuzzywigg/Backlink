#!/usr/bin/env python
"""
Example script demonstrating the Repository pattern.

This script shows how to use the repository system for managing
structured data in the Backlink Broadcast Hive.
"""

from datetime import datetime, timezone

from hive.utils.repository import HoneycombRepository, Repository


def example_basic_operations():
    """Demonstrate basic CRUD operations."""
    print("=== Basic Repository Operations ===\n")

    # Create a repository for demo purposes
    demo_repo = Repository("demo_example", base_path=None)

    # Clear any existing data
    demo_repo.clear()

    # CREATE
    print("Creating items...")
    song_id = demo_repo.create({
        "title": "Electric Dreams",
        "artist": "Synthwave Collective",
        "genre": "Electronic",
        "duration": 245,
        "plays": 0
    })
    print(f"✓ Created song with ID: {song_id}")

    # Another with custom ID
    demo_repo.create(
        {
            "title": "Neon Nights",
            "artist": "Retrowave",
            "genre": "Electronic",
            "duration": 320,
            "plays": 0
        },
        item_id="neon-001"
    )
    print("✓ Created song with custom ID: neon-001")

    # READ
    print("\nReading items...")
    song = demo_repo.get(song_id)
    if song:
        print(f"✓ Retrieved: '{song['title']}' by {song['artist']}")

    # UPDATE
    print("\nUpdating item...")
    demo_repo.update(song_id, {
        "plays": 42,
        "last_played": datetime.now(timezone.utc).isoformat()
    })
    updated = demo_repo.get(song_id)
    print(f"✓ Updated plays to: {updated['plays']}")

    # LIST
    print("\nListing all items...")
    all_songs = demo_repo.list()
    print(f"✓ Found {len(all_songs)} songs")
    for s in all_songs:
        print(f"  - {s['title']} by {s['artist']}")

    # COUNT & EXISTS
    print(f"\nTotal items in repository: {demo_repo.count()}")
    print(f"Song exists: {demo_repo.exists(song_id)}")

    # DELETE
    print("\nDeleting item...")
    demo_repo.delete(song_id)
    print(f"✓ Deleted song {song_id}")
    print(f"Remaining items: {demo_repo.count()}")

    # Clean up
    demo_repo.clear()
    print("\n✓ Repository cleared")


def example_filtering_and_pagination():
    """Demonstrate filtering and pagination."""
    print("\n\n=== Filtering and Pagination ===\n")

    repo = Repository("filter_example", base_path=None)
    repo.clear()

    # Create sample data
    print("Creating sample dataset...")
    genres = ["Rock", "Electronic", "Jazz", "Hip Hop"]
    for i in range(20):
        repo.create({
            "title": f"Track {i+1}",
            "artist": f"Artist {i+1}",
            "genre": genres[i % len(genres)],
            "plays": i * 10,
            "rating": (i % 5) + 1
        })
    print(f"✓ Created {repo.count()} tracks")

    # Filter by genre
    print("\nFiltering by genre...")
    electronic = repo.list(filter_fn=lambda x: x["genre"] == "Electronic")
    print(f"✓ Found {len(electronic)} Electronic tracks")

    # Filter by plays
    print("\nFiltering by popularity...")
    popular = repo.list(filter_fn=lambda x: x["plays"] > 100)
    print(f"✓ Found {len(popular)} tracks with >100 plays")

    # Pagination
    print("\nPagination example...")
    page_size = 5
    page_1 = repo.list(limit=page_size, offset=0)
    page_2 = repo.list(limit=page_size, offset=page_size)
    print(f"✓ Page 1: {len(page_1)} items")
    print(f"✓ Page 2: {len(page_2)} items")

    # Combined filter + pagination
    high_rated = repo.list(
        filter_fn=lambda x: x["rating"] >= 4,
        limit=3
    )
    print("\n✓ Top 3 high-rated tracks:")
    for track in high_rated:
        print(f"  - {track['title']} (rating: {track['rating']})")

    repo.clear()


def example_factory_pattern():
    """Demonstrate using the HoneycombRepository factory."""
    print("\n\n=== Repository Factory Pattern ===\n")

    # Create factory
    factory = HoneycombRepository()

    # Get multiple repositories
    print("Creating multiple repositories...")
    users = factory.get_repository("users_example")
    events = factory.get_repository("events_example")
    sessions = factory.get_repository("sessions_example")

    # Clear them
    users.clear()
    events.clear()
    sessions.clear()

    # Add data to different repositories
    print("\nAdding data to users repository...")
    user_id = users.create({
        "username": "alice",
        "role": "dj",
        "joined": datetime.now(timezone.utc).isoformat()
    })
    print(f"✓ Created user: {user_id}")

    print("\nAdding data to events repository...")
    event_id = events.create({
        "type": "song_played",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {"title": "Track 1", "artist": "Artist 1"}
    })
    print(f"✓ Created event: {event_id}")

    print("\nAdding data to sessions repository...")
    session_id = sessions.create({
        "user_id": user_id,
        "started": datetime.now(timezone.utc).isoformat(),
        "active": True
    })
    print(f"✓ Created session: {session_id}")

    # Verify isolation
    print("\nVerifying repository isolation...")
    print(f"  Users: {users.count()} items")
    print(f"  Events: {events.count()} items")
    print(f"  Sessions: {sessions.count()} items")

    # Verify factory reuses instances
    users_again = factory.get_repository("users_example")
    print(f"\nFactory reuses instances: {users is users_again}")

    # Clean up
    users.clear()
    events.clear()
    sessions.clear()


def example_real_world_use_case():
    """Demonstrate a real-world use case: tracking listener activity."""
    print("\n\n=== Real World Use Case: Listener Tracker ===\n")

    listeners = Repository("listener_tracker_example", base_path=None)
    listeners.clear()

    # Simulate listener joining
    print("Simulating listener activity...")
    listener_ids = []
    for i in range(5):
        listener_id = listeners.create({
            "username": f"node_{i+1}",
            "first_seen": datetime.now(timezone.utc).isoformat(),
            "interactions": 0,
            "favorite_genre": ["Rock", "Electronic", "Jazz"][i % 3]
        })
        listener_ids.append(listener_id)
        print(f"✓ Listener node_{i+1} joined")

    # Simulate interactions
    print("\nSimulating interactions...")
    for listener_id in listener_ids[:3]:  # Only first 3 are active
        listener = listeners.get(listener_id)
        listeners.update(listener_id, {
            "interactions": listener["interactions"] + 10,
            "last_seen": datetime.now(timezone.utc).isoformat()
        })

    # Get active listeners (>5 interactions)
    print("\nIdentifying active listeners...")
    active = listeners.list(filter_fn=lambda listener: listener["interactions"] > 5)
    print(f"✓ Found {len(active)} active listeners:")
    for listener in active:
        print(f"  - {listener['username']}: {listener['interactions']} interactions")

    # Get listeners by genre preference
    print("\nListeners who prefer Electronic music:")
    electronic_fans = listeners.list(
        filter_fn=lambda listener: listener["favorite_genre"] == "Electronic"
    )
    for fan in electronic_fans:
        print(f"  - {fan['username']}")

    # Stats
    print(f"\nTotal listeners: {listeners.count()}")
    print(f"Active rate: {len(active)/listeners.count()*100:.1f}%")

    listeners.clear()


def main():
    """Run all examples."""
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     Backlink Broadcast - Repository Pattern Demo        ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    try:
        example_basic_operations()
        example_filtering_and_pagination()
        example_factory_pattern()
        example_real_world_use_case()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
