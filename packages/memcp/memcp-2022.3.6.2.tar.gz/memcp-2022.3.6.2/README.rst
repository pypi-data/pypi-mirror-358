memcp - Memory for Model Context Protocol
=========================================

.. image:: https://readthedocs.org/projects/memcp/badge/?version=latest
    :target: https://memcp.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/memcp.svg
    :target: https://pypi.org/project/memcp/
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/memcp.svg
    :target: https://pypi.org/project/memcp/
    :alt: Python versions

``memcp`` is a Model Context Protocol (MCP) server that provides persistent memory
capabilities for AI assistants like Claude. It enables storing and retrieving
information across conversations using a local SQLite database.

Features
--------

* **Persistent Storage**: Store information that persists between conversations
* **Keyword-Based Search**: Efficiently find stored memories using keyword associations
* **Simple Key-Value Store**: Easy to use get/set operations with additional keyword metadata
* **Local SQLite Database**: All data stored locally in a SQLite database you control
* **MCP Integration**: Seamlessly integrates with Claude Desktop and other MCP clients

Installation
------------

Install from PyPI:

.. code-block:: bash

    pip install memcp

Or install from source:

.. code-block:: bash

    git clone https://github.com/moshez/memcp.git
    cd memcp
    pip install -e .

Quick Start
-----------

Configure memcp in Claude Desktop by adding it to your 
``claude_desktop_config.json``:

.. code-block:: json

    {
      "mcpServers": {
        "memcp": {
          "command": "/path/to/python",
          "args": ["-m", "memcp", "--db", "/path/to/memory.db"]
        }
      }
    }

See the `full documentation <https://memcp.readthedocs.io>`_ for detailed
configuration instructions.

Documentation
-------------

Full documentation is available at `memcp.readthedocs.io <https://memcp.readthedocs.io>`_.

Development
-----------

To set up a development environment:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/moshez/memcp.git
    cd memcp
    
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install in development mode
    pip install -e .
    
    # Install development dependencies
    pip install nox
    
    # Run tests
    nox -e tests
    
    # Run linting
    nox -e lint
    
    # Build documentation
    nox -e docs

License
-------

MIT License - see LICENSE file for details.