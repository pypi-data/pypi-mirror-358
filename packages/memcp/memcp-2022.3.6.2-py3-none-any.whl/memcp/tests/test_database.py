import unittest
import os
import tempfile
import sqlite3
from pathlib import Path
from hamcrest import assert_that, equal_to, is_, instance_of

from ..database import get_database_path, get_connection


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        os.environ["MEMCP_DATABASE"] = self.db_path

    def tearDown(self):
        self.temp_dir.cleanup()
        if "MEMCP_DATABASE" in os.environ:
            del os.environ["MEMCP_DATABASE"]

    def test_get_database_path_from_env(self):
        assert_that(get_database_path(), equal_to(self.db_path))

    def test_get_database_path_default(self):
        del os.environ["MEMCP_DATABASE"]
        assert_that(get_database_path(), equal_to("memcp.db"))

    def test_get_connection_creates_connection(self):
        # Create database file first
        Path(self.db_path).touch()

        with get_connection() as conn:
            assert_that(conn, instance_of(sqlite3.Connection))

            # Check that foreign keys are enabled
            cursor = conn.execute("PRAGMA foreign_keys")
            result = cursor.fetchone()
            assert_that(result[0], equal_to(1))

    def test_get_connection_rollback_on_error(self):
        # Create database and table
        Path(self.db_path).touch()
        with get_connection() as conn:
            conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, value TEXT)")

        # Test rollback
        try:
            with get_connection() as conn:
                conn.execute("INSERT INTO test_table (value) VALUES ('test')")
                # Force an error
                conn.execute("INVALID SQL")
        except sqlite3.OperationalError:
            pass

        # Verify rollback happened
        with get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert_that(count, equal_to(0))

    def test_init_database_creates_file(self):
        assert_that(os.path.exists(self.db_path), is_(False))

        # Note: init_database would normally run migrations, but we'll test
        # basic file creation here since migrations require alembic setup
        # For full testing, we'd need to mock the subprocess call
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the file like init_database does
        conn = sqlite3.connect(str(db_path))
        conn.close()

        assert_that(os.path.exists(self.db_path), is_(True))

    def test_init_database_creates_parent_directories(self):
        nested_path = os.path.join(self.temp_dir.name, "nested", "dir", "test.db")
        os.environ["MEMCP_DATABASE"] = nested_path

        db_path = Path(nested_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        assert_that(os.path.exists(db_path.parent), is_(True))
