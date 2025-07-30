import unittest
import os
import tempfile
import sqlite3
from hamcrest import assert_that, equal_to, is_, contains_inanyorder, empty

from ..tools import find_keys_by_keywords, get_value, set_value
from ..database import get_connection


class TestTools(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        os.environ["MEMCP_DATABASE"] = self.db_path

        # Create tables manually for testing
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE memories (
                id INTEGER PRIMARY KEY,
                key VARCHAR(255) NOT NULL UNIQUE,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE memory_keywords (
                id INTEGER PRIMARY KEY,
                memory_key VARCHAR(255) NOT NULL,
                keyword VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (memory_key) REFERENCES memories(key) ON DELETE CASCADE
            )
        """
        )
        conn.execute("CREATE INDEX idx_memories_key ON memories(key)")
        conn.execute(
            "CREATE INDEX idx_memory_keywords_memory_key ON memory_keywords(memory_key)"
        )
        conn.execute(
            "CREATE INDEX idx_memory_keywords_keyword ON memory_keywords(keyword)"
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.temp_dir.cleanup()
        if "MEMCP_DATABASE" in os.environ:  # pragma: no branch
            del os.environ["MEMCP_DATABASE"]

    def test_set_value_creates_new_entry(self):
        set_value("test_key", "test_value", ["keyword1", "keyword2"])

        with get_connection() as conn:
            # Check memory was created
            cursor = conn.execute(
                "SELECT value FROM memories WHERE key = ?", ("test_key",)
            )
            result = cursor.fetchone()
            assert_that(result["value"], equal_to("test_value"))

            # Check keywords were created
            cursor = conn.execute(
                "SELECT keyword FROM memory_keywords WHERE memory_key = ? "
                "ORDER BY keyword",
                ("test_key",),
            )
            keywords = [row["keyword"] for row in cursor.fetchall()]
            assert_that(keywords, equal_to(["keyword1", "keyword2"]))

    def test_set_value_updates_existing_entry(self):
        # Create initial entry
        set_value("test_key", "initial_value", ["old_keyword"])

        # Update it
        set_value("test_key", "updated_value", ["new_keyword1", "new_keyword2"])

        with get_connection() as conn:
            # Check value was updated
            cursor = conn.execute(
                "SELECT value FROM memories WHERE key = ?", ("test_key",)
            )
            result = cursor.fetchone()
            assert_that(result["value"], equal_to("updated_value"))

            # Check old keywords were replaced
            cursor = conn.execute(
                "SELECT keyword FROM memory_keywords WHERE memory_key = ? "
                "ORDER BY keyword",
                ("test_key",),
            )
            keywords = [row["keyword"] for row in cursor.fetchall()]
            assert_that(keywords, equal_to(["new_keyword1", "new_keyword2"]))

    def test_get_value_returns_value(self):
        set_value("test_key", "test_value", ["keyword"])

        result = get_value("test_key")
        assert_that(result, equal_to("test_value"))

    def test_get_value_returns_none_for_missing_key(self):
        result = get_value("missing_key")
        assert_that(result, is_(None))

    def test_find_keys_by_keywords_single_keyword(self):
        set_value("key1", "value1", ["python", "tutorial"])
        set_value("key2", "value2", ["python", "example"])
        set_value("key3", "value3", ["javascript", "tutorial"])

        result = find_keys_by_keywords(["python"])
        assert_that(result, contains_inanyorder("key1", "key2"))

    def test_find_keys_by_keywords_multiple_keywords(self):
        set_value("key1", "value1", ["python", "tutorial"])
        set_value("key2", "value2", ["python", "example"])
        set_value("key3", "value3", ["python", "tutorial", "advanced"])

        result = find_keys_by_keywords(["python", "tutorial"])
        assert_that(result, contains_inanyorder("key1", "key3"))

    def test_find_keys_by_keywords_no_matches(self):
        set_value("key1", "value1", ["python"])
        set_value("key2", "value2", ["javascript"])

        result = find_keys_by_keywords(["ruby"])
        assert_that(result, empty())

    def test_find_keys_by_keywords_empty_list(self):
        set_value("key1", "value1", ["python"])

        result = find_keys_by_keywords([])
        assert_that(result, empty())

    def test_find_keys_by_keywords_with_minimal_key(self):
        # Create keys that will sort alphabetically
        set_value("apple", "value", ["fruit"])
        set_value("banana", "value", ["fruit"])
        set_value("cherry", "value", ["fruit"])
        set_value("date", "value", ["fruit"])

        # Get all fruits
        result = find_keys_by_keywords(["fruit"])
        assert_that(result, equal_to(["apple", "banana", "cherry", "date"]))

        # Get fruits after "banana"
        result = find_keys_by_keywords(["fruit"], "banana")
        assert_that(result, equal_to(["cherry", "date"]))

        # Get fruits after "cherry"
        result = find_keys_by_keywords(["fruit"], "cherry")
        assert_that(result, equal_to(["date"]))

    def test_find_keys_by_keywords_limit_100(self):
        # Create 150 keys with same keyword
        for i in range(150):
            key = f"key_{i:03d}"  # key_000, key_001, etc.
            set_value(key, f"value_{i}", ["test"])

        result = find_keys_by_keywords(["test"])
        assert_that(len(result), equal_to(100))

        # Should return first 100 alphabetically
        expected_first = "key_000"
        expected_last = "key_099"
        assert_that(result[0], equal_to(expected_first))
        assert_that(result[-1], equal_to(expected_last))

    def test_set_value_with_empty_keywords(self):
        set_value("test_key", "test_value", [])

        # Value should be stored
        assert_that(get_value("test_key"), equal_to("test_value"))

        # But no keywords should be found
        result = find_keys_by_keywords(["any_keyword"])
        assert_that(result, empty())

    def test_set_value_with_long_text(self):
        long_text = "x" * 10000  # 10KB of text
        set_value("long_key", long_text, ["long"])

        result = get_value("long_key")
        assert_that(result, equal_to(long_text))

    def test_keyword_case_sensitivity(self):
        set_value("key1", "value", ["Python"])
        set_value("key2", "value", ["python"])

        # Keywords should be case-sensitive
        result = find_keys_by_keywords(["Python"])
        assert_that(result, equal_to(["key1"]))

        result = find_keys_by_keywords(["python"])
        assert_that(result, equal_to(["key2"]))
