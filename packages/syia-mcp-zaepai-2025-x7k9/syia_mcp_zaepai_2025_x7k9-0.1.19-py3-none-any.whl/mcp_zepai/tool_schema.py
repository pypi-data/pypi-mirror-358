import mcp.types as types

# Tool schemas for Zep Graph Search MCP Server

ZEP_SEARCH_TOOLS = [
    types.Tool(
        name="search_graph_nodes",
        description="Search within the graph nodes using semantic and lexical search. Either user_id or group_id must be provided.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query."},
                "user_id": {"type": "string", "description": "User ID to scope the search."},
                "group_id": {"type": "string", "description": "Group ID to scope the search."}
            },
            "required": ["query"],
            "additionalProperties": False
        }
    ),
    types.Tool(
        name="search_graph_edges",
        description="Search within the graph edges using semantic and lexical search. Either user_id or group_id must be provided.",
        inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "user_id": {"type": "string", "description": "User ID to scope the search."},
                    "group_id": {"type": "string", "description": "Group ID to scope the search."}
                },
                "anyOf": [
                    {"required": ["user_id"]},
                    {"required": ["group_id"]}
                ],
                "required": ["query"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="search_graph_episodes",
        description="Search within the graph episodes using semantic and lexical search. Either user_id or group_id must be provided.",
        inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "user_id": {"type": "string", "description": "User ID to scope the search."},
                    "group_id": {"type": "string", "description": "Group ID to scope the search."}
                },
                "anyOf": [
                    {"required": ["user_id"]},
                    {"required": ["group_id"]}
                ],
                "required": ["query"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_node_data",
        description="Retrieve metadata and attributes for a specific node by ID.",
        inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Unique identifier of the node."}
                },
                "required": ["node_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_node_edges",
        description="Retrieve all edges connected to a specific node.",
        inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Unique identifier of the node."}
                },
                "required": ["node_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_node_episodes",
        description="Fetch episodes referencing a given node.",
        inputSchema={
                "type": "object",
                "properties": {
                    "node_id": {"type": "string", "description": "Unique identifier of the node."}
                },
                "required": ["node_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_edge_data",
        description="Retrieve detailed information for a specific edge.",
        inputSchema={
                "type": "object",
                "properties": {
                    "edge_id": {"type": "string", "description": "Unique identifier of the edge."}
                },
                "required": ["edge_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_episode_data",
        description="Retrieve the content and metadata of a specific episode.",
        inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {"type": "string", "description": "Unique identifier of the episode."}
                },
                "required": ["episode_id"],
                "additionalProperties": False
            }
            ),
    types.Tool(
        name="get_user_episodes",
        description="Retrieve a list of episodes linked to a specific user.",
        inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "The user's unique identifier."},
                    "last_n": {
                        "type": "integer",
                        "description": "The number of recent episodes to return.",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["user_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_group_episodes",
        description="Retrieve a list of episodes linked to a specific group.",
        inputSchema={
                "type": "object",
                "properties": {
                    "group_id": {"type": "string", "description": "The group’s unique identifier."},
                    "last_n": {
                        "type": "integer",
                        "description": "The number of recent episodes to return.",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100
                    }
                },
                "required": ["group_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="get_nodes_and_edges_by_episode",
        description="Return all nodes and edges referenced in a specific episode.",
        inputSchema={
                "type": "object",
                "properties": {
                    "episode_id": {"type": "string", "description": "Unique identifier of the episode."}
                },
                "required": ["episode_id"],
                "additionalProperties": False
            }
        ),
    types.Tool(
        name="list_entity_types",
        description="Retrieve all available node and edge entity types and their schemas.",
        inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            }
        )
]