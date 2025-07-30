"""memcp - Memory for Model Context Protocol.

This package provides a Model Context Protocol (MCP) server that enables
persistent memory capabilities for AI assistants like Claude. It allows
storing and retrieving key-value pairs with associated keywords for
efficient searching.

The main components are:

- :mod:`memcp.database`: Database connection and initialization
- :mod:`memcp.tools`: Core memory operations
    (find_keys_by_keywords, get_value, set_value)
- :mod:`memcp.mcp_server`: MCP server implementation

Example usage as an MCP server::

    python -m memcp --db /path/to/memory.db

This will start the MCP server which exposes three tools:

- mcp_find_keys_by_keywords: Search for memory keys by keywords
- mcp_get_value: Retrieve a value by its key
- mcp_set_value: Store or update a value with keywords
"""

import importlib.metadata
from gather import entry

__version__ = importlib.metadata.version(__name__)

ENTRY_DATA = entry.EntryData.create(__name__)
