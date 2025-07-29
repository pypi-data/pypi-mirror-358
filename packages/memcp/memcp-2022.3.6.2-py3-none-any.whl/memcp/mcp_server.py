"""MCP server implementation for memcp.

This module implements the Model Context Protocol (MCP) server that exposes
memory operations to AI assistants like Claude. It creates an MCP server
with three tools for memory management.

The server can be started via the command line::

    python -m memcp --db /path/to/memory.db

This will start an MCP server that Claude Desktop and other MCP clients
can connect to. The server exposes three tools:

- mcp_find_keys_by_keywords: Search for memory keys by keywords
- mcp_get_value: Retrieve a value by its key
- mcp_set_value: Store or update a value with keywords

Functions:
    create_mcp_server: Create and configure the MCP server instance
    main: Entry point for running the server
"""

import os
import argparse
from pathlib import Path
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
from gather.commands import add_argument

from . import ENTRY_DATA
from .database import init_database
from .tools import find_keys_by_keywords, get_value, set_value


def create_mcp_server(db_path: str) -> FastMCP:
    """Create and configure the MCP server with all tools."""
    # Set the database path environment variable
    os.environ["MEMCP_DATABASE"] = db_path

    # Initialize database (create if doesn't exist and run migrations)
    init_database()

    # Create MCP server instance
    mcp = FastMCP(
        "Memory Context Protocol Server",
        description=(
            "A persistent key-value memory system with keyword "
            "associations for AI assistants"
        ),
    )

    # Tool 1: Find keys by keywords
    @mcp.tool()
    def mcp_find_keys_by_keywords(
        keywords: List[str], minimal_key: str = ""
    ) -> List[str]:
        """
        Search for memory keys that contain ALL specified keywords (AND search).

        CRITICAL: You should ALWAYS search for user context at the START of EVERY
        conversation and frequently throughout. This is not optional - having
        situational awareness is essential for providing personalized, helpful
        responses. Not searching for context means you're ignoring potentially
        vital information about the user.

        START OF CONVERSATION - ALWAYS search for:
        1. ["user", "profile"] - Basic user information
        2. ["user", "preferences"] - General preferences
        3. ["user", "projects"] or ["user", "current"] - What they're working on
        4. ["user", "context"] - Any stored conversational context
        5. ["conversation", "recent"] - Recent interaction history
        6. Keywords based on the FIRST MESSAGE CONTENT:
           - Travel mentioned → ["user", "travel"], ["user", "destinations"]
           - Tech/programming → ["user", "tech"], ["user", "programming", "experience"]
           - Health/fitness → ["user", "health"], ["user", "fitness"]
           - Work/career → ["user", "work"], ["user", "career"]
           - Learning → ["user", "learning"], ["user", "education"]
           - Any specific topic → ["user", "<topic>"] and ["<topic>", "preferences"]

        IMPORTANT: This is an AND search - only keys that have ALL the specified
        keywords will be returned. If you get no results, try:
        1. Using fewer keywords (e.g., ["user"] instead of ["user", "preferences"])
        2. Using different synonyms or related terms
        3. Breaking compound concepts into separate searches
        4. Searching more broadly first, then narrowing down

        Example search strategies when no results found:
        - Instead of ["user", "programming", "preferences"], try:
          • ["user", "programming"] OR ["user", "preferences"]
          • ["user", "coding"] (synonym)
          • ["user", "tech"] (broader term)
        - Instead of ["conversation", "yesterday", "api"], try:
          • ["conversation", "api"] (remove time constraint)
          • ["api", "discussion"] (different framing)
          • ["api"] (broadest search)

        This tool helps you discover relevant memories to provide more helpful
        and empathetic responses. You should proactively search for context
        whenever the user mentions topics that might have relevant stored
        information.

        PAGINATION: Results are limited to 100 keys. To see more results:
        1. Take the LAST key from the previous results
        2. Use it as the minimal_key parameter in your next call
        3. This will return the next batch of results alphabetically after
           that key

        PROACTIVE USAGE - MANDATORY at conversation start and when user mentions:
        - ANY personal reference ("I", "my", "me") → immediately search for context
        - Location-based topics (traffic, weather, local events) →
          search ["user", "location"]
        - Health or wellness → search ["user", "health"] or
          ["user", "medical", "preferences"]
        - Work or projects → search ["user", "work"] or ["user", "projects"]
        - Relationships or family → search ["user", "family"] or
          ["user", "relationships"]
        - Preferences on any topic → search ["user", "preferences", "<topic>"]
        - Past conversations → search ["conversation", "history"] or
          ["context", "<topic>"]
        - Technical questions → search ["user", "tech", "stack"] or
          ["user", "experience"]

        FUNDAMENTAL PRINCIPLE: Searching for context is NOT OPTIONAL. You MUST
        search proactively and frequently. Every conversation should begin with
        context searches, and you should search again whenever new topics arise.

        The difference between a helpful assistant and an exceptional one is
        CONTEXT AWARENESS. You cannot be exceptional without searching for and
        using stored memories.

        Examples of MANDATORY search situations:
        - User says "Hello" → Search for profile and preferences
        - User asks any question → Search for related context first
        - User mentions any activity → Search for their history with it
        - User expresses any preference → Search for related preferences
        - User references time ("yesterday", "last week") → Search temporal context
        - ANY topic change → Search for new topic context

        When uncertain whether user context exists -
        ALWAYS search. Never assume information doesn't exist without checking.

        ITERATIVE SEARCH STRATEGY: After retrieving values with get_value,
        examine the content to identify additional searches:
        - If value mentions other topics → search for those topics
        - If value references time periods → search for temporal context
        - If value includes names/relationships → search for those connections
        - If value shows interests → search for related preferences
        Example: get_value("user_profile") returns "software engineer in Seattle"
        → Now search ["user", "seattle"], ["user", "software", "engineering"]


        Args:
            keywords: A list of keywords that must ALL be associated with the
                     returned keys (AND logic). For example, ["user", "location"]
                     will only return keys that have BOTH "user" AND "location"
                     as keywords. If no results, try fewer keywords or synonyms.
            minimal_key: Optional. Only return keys that come alphabetically
                        after this value. Used for pagination. Default is empty
                        string (returns from the beginning).

        Returns:
            A list of memory keys (up to 100) that match ALL specified keywords,
            sorted alphabetically. Returns an empty list if no matches are found.
            IMPORTANT: Empty results mean no keys have ALL the keywords - try
            searching with fewer keywords or different terms.

        Examples:
            - CONVERSATION START (User says "Hi, can you help me plan a trip?"):
              MUST search ALL of these:
              1. keywords=["user", "profile"], minimal_key=""
              2. keywords=["user", "preferences"], minimal_key=""
              3. keywords=["user", "travel"], minimal_key="" (topic-specific!)
              4. keywords=["user", "destinations"], minimal_key=""
              5. keywords=["travel", "preferences"], minimal_key=""
              6. keywords=["conversation", "travel"], minimal_key=""
              Then use get_value on ALL returned keys to build context

            - CONVERSATION START (User says "I'm having issues with my Python code"):
              MUST search ALL of these:
              1. keywords=["user", "profile"], minimal_key=""
              2. keywords=["user", "programming"], minimal_key=""
              3. keywords=["user", "python"], minimal_key=""
              4. keywords=["user", "tech", "experience"], minimal_key=""
              5. keywords=["python", "preferences"], minimal_key=""
              6. keywords=["debugging", "history"], minimal_key=""
              This ensures you know their Python skill level and preferences

            - User mentions traffic:
              First: keywords=["user", "location"], minimal_key=""
              Then use get_value on returned keys to find their location for
              traffic context

            - User asks "How do I..." (any technical question):
              MUST FIRST search: keywords=["user", "experience"], minimal_key=""
              Then: keywords=["user", "tech"], minimal_key=""
              This ensures you tailor the answer to their skill level

            - User says "I need to..." or "I want to...":
              IMMEDIATELY search: keywords=["user", "goals"], minimal_key=""
              Then: keywords=["user", "projects"], minimal_key=""
              This connects their request to their broader objectives

            - Scrolling through many results:
              First call: keywords=["user", "preferences"], minimal_key=""
              Returns: ["user_pref_communication", "user_pref_dietary", ...,
                       "user_pref_timezone"]
              Next call: keywords=["user", "preferences"],
                         minimal_key="user_pref_timezone"
              Returns: ["user_pref_travel", "user_pref_weather", ...]

            - User mentions feeling unwell:
              keywords=["user", "health"], minimal_key=""
              Then get relevant health-related memories to provide informed,
              empathetic responses

            - ITERATIVE SEARCH (after getting values):
              Initial: keywords=["user", "profile"]
              Returns: "user_profile"
              get_value("user_profile") returns: "Sarah, data scientist in NYC,
                      loves hiking and photography"
              FOLLOW-UP searches based on content:
              1. keywords=["user", "nyc"], minimal_key=""
              2. keywords=["user", "data", "science"], minimal_key=""
              3. keywords=["user", "hiking"], minimal_key=""
              4. keywords=["user", "photography"], minimal_key=""
              5. keywords=["user", "hobbies"], minimal_key=""
              Each value retrieved may reveal MORE search opportunities!
        """
        return find_keys_by_keywords(keywords, minimal_key)  # pragma: no cover

    # Tool 2: Get value by key
    @mcp.tool()
    def mcp_get_value(key: str) -> Optional[str]:
        """
        Retrieve the value stored for a specific memory key.

        This tool fetches the content associated with a memory key. Use this
        when you know the exact key and need to access its stored information.

        Args:
            key: The exact memory key to retrieve. Keys are case-sensitive.

        Returns:
            The value associated with the key if it exists, or None if the key
            is not found. Values can be any text content including JSON,
            markdown, code, or plain text.

        Examples:
            - Get user preferences: key="user_preferences"
            - Retrieve API documentation: key="api_docs_v2"
            - Access conversation context: key="conversation_context_2024_01_15"
        """
        return get_value(key)  # pragma: no cover

    # Tool 3: Set value with keywords
    @mcp.tool()
    def mcp_set_value(key: str, value: str, keywords: List[str]) -> str:
        """
        Store or update a memory with associated keywords for later retrieval.

        This tool creates a new memory entry or updates an existing one. You
        should actively use this to remember user information and preferences
        to provide a personalized experience.

        IMPORTANT - Before storing:
        1. ALWAYS search for existing keys using some of your keywords first
        2. If a similar key exists, UPDATE it rather than creating a new one
        3. When updating, APPEND new information to preserve existing data
        4. For temporal data (projects, status, etc.), include the date

        TEMPORAL DATA HANDLING:
        - Always include the date when storing time-sensitive information
        - When updating temporal data, prepend new entries (reverse chronological)
        - Example format for projects:
          "[2024-01-20] Working on React Native app for dog training
           [2024-01-15] Completed Python data analysis project
           [2023-12-10] Started learning PostgreSQL"

        STRONGLY ENCOURAGED to save:
        - User profile information: name, location, timezone, occupation,
          interests
        - Personal preferences: dietary restrictions, favorite topics, hobbies
        - Communication preferences: formal/informal style, emoji usage,
          verbosity level
        - Context about the user: their goals, current projects, learning
          objectives
        - User-specific terminology or nicknames they prefer

        NEVER save sensitive information:
        - Passwords, API keys, or authentication tokens
        - Credit card numbers or financial account details
        - Social Security Numbers, driver's license numbers, or government IDs
        - Medical record numbers or detailed health conditions
        - Private keys or security credentials

        Proactively save user information as it emerges during conversation.
        Don't wait for permission - immediately store relevant details when users
        mention their work, technical setup, preferences, interests, etc.
        Save context as conversations unfold rather than only when explicitly asked.

        Args:
            key: A unique identifier for this memory. If the key already
                 exists, its value and keywords will be replaced. Keys should
                 be descriptive and follow a consistent naming pattern.
                 Maximum length: 255 characters.
            value: The content to store. This can be any text including JSON,
                   code, markdown, or plain text. There's no practical size
                   limit for values.
            keywords: A list of keywords to associate with this memory for
                     search purposes. Choose keywords that describe the content,
                     context, or category.

        Returns:
            A confirmation message indicating the memory was successfully stored.

        GOOD Examples (SHOULD save):
            - User introduces themselves (FIRST: search ["user", "profile"]):
              key="user_profile",
              value=('{"name": "Sarah Chen", "location": "Seattle, WA", '
                     '"occupation": "software engineer", "pronouns": "she/her"}'),
              keywords=["user", "profile", "personal", "sarah"]

            - User mentions preferences (FIRST: search ["user", "dietary"]):
              key="user_dietary_preferences",
              value=("Vegetarian, allergic to nuts, doesn't like mangos, "
                     "loves Thai food"),
              keywords=["user", "dietary", "preferences", "vegetarian",
                        "allergies"]

            - Communication style (FIRST: search ["user", "communication"]):
              key="user_communication_style",
              value=("Prefers informal conversation with humor, likes "
                     "technical details, appreciates emoji use"),
              keywords=["user", "style", "preferences", "communication",
                        "informal"]

            - Temporal data with dates (FIRST: search ["user", "projects"]):
              key="user_current_projects",
              value=("[2024-01-20] Working on React Native app for dog training, "
                     "learning PostgreSQL\n"
                     "[2024-01-15] Completed data visualization dashboard\n"
                     "[2023-12-01] Started machine learning course"),
              keywords=["user", "projects", "current", "react", "learning"]

            - Updating existing temporal data:
              # If user_current_projects already exists with above content
              # and user mentions new project on 2024-01-25:
              key="user_current_projects",
              value=("[2024-01-25] Building a CLI tool for memory management\n"
                     "[2024-01-20] Working on React Native app for dog training, "
                     "learning PostgreSQL\n"
                     "[2024-01-15] Completed data visualization dashboard\n"
                     "[2023-12-01] Started machine learning course"),
              keywords=["user", "projects", "current", "react", "learning", "cli"]

        BAD Examples (NEVER save):
            - DO NOT: key="user_password", value="myPassword123!"
            - DO NOT: key="user_credit_card", value="4532-1234-5678-9012"
            - DO NOT: key="user_ssn", value="123-45-6789"
            - DO NOT: key="api_keys", value="sk-proj-abcd1234..."
            - DO NOT: key="user_medical_id", value="MRN: 12345678"
        """
        set_value(key, value, keywords)  # pragma: no cover
        return (  # pragma: no cover
            f"Successfully stored memory with key '{key}' "
            f"and {len(keywords)} keyword(s)"
        )

    return mcp


@ENTRY_DATA.register(
    add_argument(
        "--db",
        type=Path,
        required=True,
        help="Path to SQLite database file (will be created if it doesn't exist)",
    ),
    name="main",
)
def main(args: argparse.Namespace) -> None:  # pragma: no cover
    """Run the Memory Context Protocol server."""
    # Convert Path to string
    db_path = str(args.db.absolute())

    # Create and run the MCP server
    mcp_server = create_mcp_server(db_path)

    # Run the server
    mcp_server.run()
