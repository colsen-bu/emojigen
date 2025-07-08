#!/usr/bin/env python3
"""Test script for static emoji functionality."""

import glob
import os


def get_static_emoji_files():
    """Get list of static emoji files from the static folder."""
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    if not os.path.exists(static_folder):
        return []

    # Support common image formats
    patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif"]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(static_folder, pattern)))

    # Sort files and return just the filenames
    return sorted([os.path.basename(f) for f in files])


def search_static_emojis(query):
    """Search static emoji files by query string."""
    all_files = get_static_emoji_files()
    if not query.strip():
        return all_files[:25]  # Return first 25 if no query

    query_lower = query.lower()

    # Search for files that contain the query in their name
    matches = []
    for filename in all_files:
        if query_lower in filename.lower():
            matches.append(filename)

    return matches[:25]  # Limit to 25 results for Discord select menu


def test_static_emoji_functions():
    """Test the static emoji helper functions."""
    print("Testing static emoji functionality...")

    # Test getting all static emoji files
    all_files = get_static_emoji_files()
    print(f"✅ Found {len(all_files)} static emoji files")

    if all_files:
        print(f"📁 First 5 files: {all_files[:5]}")

    # Test search functionality
    test_queries = ["cat", "smile", "logo", "pixel", ""]

    for query in test_queries:
        results = search_static_emojis(query)
        print(f"🔍 Search '{query}': {len(results)} results")
        if results:
            print(f"   First result: {results[0]}")

    print("\n✅ Static emoji functionality test completed!")


if __name__ == "__main__":
    test_static_emoji_functions()
