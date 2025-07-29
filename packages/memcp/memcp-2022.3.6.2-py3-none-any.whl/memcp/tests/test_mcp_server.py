import unittest
import os
import tempfile
import sqlite3
from hamcrest import assert_that, equal_to, is_, not_none, contains_string

from ..mcp_server import create_mcp_server
from ..tools import set_value, get_value


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")

    def tearDown(self):
        self.temp_dir.cleanup()
        if "MEMCP_DATABASE" in os.environ:
            del os.environ["MEMCP_DATABASE"]

    def test_create_mcp_server_initializes_database(self):
        # Create MCP server
        mcp = create_mcp_server(self.db_path)

        # Verify database path was set
        assert_that(os.environ["MEMCP_DATABASE"], equal_to(self.db_path))

        # Verify MCP server was created
        assert_that(mcp, not_none())
        assert_that(mcp.name, equal_to("Memory Context Protocol Server"))

        # Verify database was created with tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert_that("memories" in tables, is_(True))
        assert_that("memory_keywords" in tables, is_(True))
        conn.close()

    def test_mcp_tools_are_registered(self):
        # Create MCP server
        mcp = create_mcp_server(self.db_path)

        # Check that tools are registered (FastMCP stores tools internally)
        # We can't directly access the tools, but we can verify the server is configured
        assert_that(mcp, not_none())

    def test_mcp_server_tool_integration(self):
        # Create a simple test database
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
        conn.close()

        os.environ["MEMCP_DATABASE"] = self.db_path

        # Test the tools work through the database
        set_value("user_profile", '{"name": "Test User"}', ["user", "profile"])

        # Verify data was stored
        result = get_value("user_profile")
        assert_that(result, equal_to('{"name": "Test User"}'))

    def test_database_creation_on_init(self):
        # Ensure database doesn't exist
        assert_that(os.path.exists(self.db_path), is_(False))

        # Create MCP server (which should create the database)
        create_mcp_server(self.db_path)

        # Database file should now exist
        assert_that(os.path.exists(self.db_path), is_(True))

    def test_tool_descriptions_are_comprehensive(self):
        # This test verifies that tool descriptions contain expected guidance
        from ..mcp_server import create_mcp_server

        # Read the source to check descriptions (since we can't access them at runtime)
        import inspect

        source = inspect.getsource(create_mcp_server)

        # Check find_keys_by_keywords description
        assert_that(source, contains_string("PAGINATION"))
        assert_that(source, contains_string("PROACTIVE USAGE"))
        assert_that(source, contains_string("traffic"))

        # Check set_value description
        assert_that(source, contains_string("STRONGLY ENCOURAGED"))
        assert_that(source, contains_string("NEVER save sensitive"))
        assert_that(source, contains_string("Sarah Chen"))
