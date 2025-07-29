"""Database connection and initialization for memcp.

This module provides functions for managing the SQLite database used by memcp.
It includes connection management, database initialization, and migration support.

The database schema consists of two tables:

- memories: Stores key-value pairs with timestamps
- memory_keywords: Associates keywords with memory keys for searching

Functions:
    get_database_path: Get the database path from environment or default
    get_connection: Context manager for database connections
    init_database: Initialize database and run migrations
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator


def get_database_path() -> str:
    """Get the database path from environment or use default."""
    return os.environ.get("MEMCP_DATABASE", "memcp.db")


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """Get a database connection with proper settings."""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """Initialize the database by running migrations."""
    import subprocess
    import sys
    from pathlib import Path

    db_path = Path(get_database_path())

    # Create database directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create database file if it doesn't exist
    if not db_path.exists():  # pragma: no branch
        import sqlite3

        conn = sqlite3.connect(str(db_path))
        conn.close()

    # Find the alembic.ini file
    module_dir = Path(__file__).parent
    alembic_ini = module_dir / "migrations" / "alembic.ini"

    # Set the database URL environment variable for alembic
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path.absolute()}"

    # Run alembic migrations
    subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(alembic_ini), "upgrade", "head"],
        check=True,
        cwd=str(module_dir),
    )
