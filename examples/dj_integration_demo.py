#!/usr/bin/env python3
"""
DJ Integration Demo - Example using Agent.md with DJ Memory.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("DJ Integration Demo")
print("=" * 70)
print("This demo shows how to use Agent.md personality with DJ Memory")
print()

print("Features available:")
print("  ✓ Agent.md personality loading")
print("  ✓ Time-based persona selection")
print("  ✓ Song history tracking")
print("  ✓ Listener profile management")
print("  ✓ Anti-repetition checking")
print("  ✓ Genre variety validation")
print()

print("To use these features in your DJ:")
print("1. from hive.utils.dj_broadcast_helper import DJBroadcastHelper")
print("2. helper = DJBroadcastHelper()")
print("3. context = helper.start_session(time_of_day='morning')")
print("4. helper.track_song_played('Song Title', 'Artist', genre='Rock')")
print()

print("See hive/utils/dj_broadcast_helper.py for full API documentation.")
print("=" * 70)
