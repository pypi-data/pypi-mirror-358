"""Core memory operations for memcp.

This module implements the main memory operations: storing, retrieving,
and searching for memories. These functions are used by the MCP server
to provide memory capabilities to AI assistants.

The module provides three main functions:

- find_keys_by_keywords: Search for memory keys by keywords
- get_value: Retrieve a value by its key
- set_value: Store or update a value with keywords

All operations use the SQLite database configured via the MEMCP_DATABASE
environment variable.
"""

from typing import List, Optional
from .database import get_connection


def find_keys_by_keywords(keywords: List[str], minimal_key: str = "") -> List[str]:
    """
    Find all keys that have ALL of the specified keywords.

    Args:
        keywords: List of keywords to search for
        minimal_key: Return only keys alphabetically after this value

    Returns:
        List of keys (up to 100) sorted alphabetically
    """
    if not keywords:
        return []

    with get_connection() as conn:
        # Build query to find keys that have ALL keywords
        placeholders = ",".join(["?" for _ in keywords])
        query = f"""
        SELECT DISTINCT m.key
        FROM memories m
        WHERE m.key > ?
        AND m.key IN (
            SELECT mk.memory_key
            FROM memory_keywords mk
            WHERE mk.keyword IN ({placeholders})
            GROUP BY mk.memory_key
            HAVING COUNT(DISTINCT mk.keyword) = ?
        )
        ORDER BY m.key
        LIMIT 100
        """

        params = [minimal_key] + keywords + [len(keywords)]
        cursor = conn.execute(query, params)
        return [row["key"] for row in cursor.fetchall()]


def get_value(key: str) -> Optional[str]:
    """
    Get the value associated with a key.

    Args:
        key: The key to look up

    Returns:
        The value if found, None otherwise
    """
    with get_connection() as conn:
        cursor = conn.execute("SELECT value FROM memories WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row["value"] if row else None


def set_value(key: str, value: str, keywords: List[str]) -> None:
    """
    Set or update a key-value pair with associated keywords.

    Args:
        key: The key to set
        value: The value to associate with the key
        keywords: List of keywords to associate with the key
    """
    with get_connection() as conn:
        # Check if key exists
        cursor = conn.execute("SELECT 1 FROM memories WHERE key = ?", (key,))
        exists = cursor.fetchone() is not None

        if exists:
            # Update existing value
            conn.execute(
                "UPDATE memories SET value = ?, updated_at = CURRENT_TIMESTAMP "
                "WHERE key = ?",
                (value, key),
            )
            # Delete existing keywords
            conn.execute("DELETE FROM memory_keywords WHERE memory_key = ?", (key,))
        else:
            # Insert new key-value pair
            conn.execute(
                "INSERT INTO memories (key, value) VALUES (?, ?)", (key, value)
            )

        # Insert keywords
        if keywords:
            conn.executemany(
                "INSERT INTO memory_keywords (memory_key, keyword) VALUES (?, ?)",
                [(key, keyword) for keyword in keywords],
            )
