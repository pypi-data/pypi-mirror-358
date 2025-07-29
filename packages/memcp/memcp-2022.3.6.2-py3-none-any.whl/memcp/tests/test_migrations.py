import unittest
import os
import tempfile
import sqlite3
import subprocess
import sys
from pathlib import Path
from hamcrest import assert_that, equal_to, is_, not_none, contains_string


class TestMigrations(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        os.environ["DATABASE_URL"] = f"sqlite:///{self.db_path}"

    def tearDown(self):
        self.temp_dir.cleanup()
        if "DATABASE_URL" in os.environ:  # pragma: no branch
            del os.environ["DATABASE_URL"]

    def test_migrations_create_memories_table(self):
        # Run migrations
        module_dir = Path(__file__).parent.parent
        alembic_ini = module_dir / "migrations" / "alembic.ini"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )

        # Check migrations ran successfully
        assert_that(
            result.returncode, equal_to(0), f"Migration failed: {result.stderr}"
        )

        # Verify memories table exists with correct schema
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='memories'
        """
        )
        create_sql = cursor.fetchone()[0]

        assert_that(create_sql, not_none())
        assert_that(create_sql.lower(), contains_string("id"))
        assert_that(create_sql.lower(), contains_string("key"))
        assert_that(create_sql.lower(), contains_string("value"))
        assert_that(create_sql.lower(), contains_string("created_at"))
        assert_that(create_sql.lower(), contains_string("updated_at"))

        conn.close()

    def test_migrations_create_memory_keywords_table(self):
        # Run migrations
        module_dir = Path(__file__).parent.parent
        alembic_ini = module_dir / "migrations" / "alembic.ini"

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )

        assert_that(result.returncode, equal_to(0))

        # Verify memory_keywords table exists
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT sql FROM sqlite_master
            WHERE type='table' AND name='memory_keywords'
        """
        )
        create_sql = cursor.fetchone()[0]

        assert_that(create_sql, not_none())
        assert_that(create_sql.lower(), contains_string("memory_key"))
        assert_that(create_sql.lower(), contains_string("keyword"))

        conn.close()

    def test_migrations_create_indexes(self):
        # Run migrations
        module_dir = Path(__file__).parent.parent
        alembic_ini = module_dir / "migrations" / "alembic.ini"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )

        # Check indexes exist
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='index' AND name LIKE 'idx_%'
        """
        )
        indexes = [row[0] for row in cursor.fetchall()]

        expected_indexes = [
            "idx_memories_key",
            "idx_memory_keywords_memory_key",
            "idx_memory_keywords_keyword",
            "idx_memory_keywords_key_keyword",
        ]

        for idx in expected_indexes:
            assert_that(idx in indexes, is_(True), f"Missing index: {idx}")

        conn.close()

    def test_foreign_key_constraint(self):
        # Run migrations
        module_dir = Path(__file__).parent.parent
        alembic_ini = module_dir / "migrations" / "alembic.ini"

        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )

        # Test foreign key constraint
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")

        # Insert a memory
        conn.execute(
            "INSERT INTO memories (key, value) VALUES ('test_key', 'test_value')"
        )

        # Try to insert keyword with non-existent memory_key
        try:
            conn.execute(
                "INSERT INTO memory_keywords (memory_key, keyword) "
                "VALUES ('nonexistent', 'keyword')"
            )
            conn.commit()  # pragma: no cover
            assert (
                False
            ), "Foreign key constraint should have failed"  # pragma: no cover
        except sqlite3.IntegrityError:
            # Expected behavior
            pass

        conn.close()

    def test_migration_idempotency(self):
        # Run migrations twice - should be idempotent
        module_dir = Path(__file__).parent.parent
        alembic_ini = module_dir / "migrations" / "alembic.ini"

        # First run
        result1 = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )
        assert_that(result1.returncode, equal_to(0))

        # Second run - should succeed without errors
        result2 = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(alembic_ini),
                "upgrade",
                "head",
            ],
            capture_output=True,
            text=True,
            cwd=str(module_dir),
        )
        assert_that(result2.returncode, equal_to(0))
