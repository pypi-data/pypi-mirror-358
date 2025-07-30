import mcp.types as types

# Tool schemas for Zep Graph Search MCP Server

ZEP_SEARCH_TOOLS = [
    types.Tool(
        name="search_graph_nodes",
        description="Search within graph nodes, where each node represents a distinct entity such as a concept, document, user-generated artifact, or data point. Enables semantic and lexical search within scoped entities. Either user_id or group_id must be provided.",
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
        description="Search within graph edges, where each edge denotes a semantic or logical relationship between two nodes (e.g., 'authored by', 'linked to', 'derived from'). Facilitates discovery of connections across entities. Either user_id or group_id must be provided.",
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
        description="Search within graph episodes, where each episode denotes a bounded sequence of interactions, events, or changes over time involving nodes and/or edges. Useful for retrieving contextualized timelines or sessions. Either user_id or group_id must be provided.",
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
        name="get_connected_edges_for_node",
        description="Retrieve all edges connected to a specified node. Useful for understanding relationships and traversing the graph structure.",
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
        name="get_episodes_for_node",
        description="Retrieve all episodes that reference a specific node. Useful for contextualizing the node within its interaction history..",
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
        name="list_latest_user_episodes",
        description="Retrieve the most recent episodes associated with a specific user. Supports pagination via last_n..",
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
        name="list_latest_group_episodes",
        description="Retrieve the most recent episodes associated with a specific group. Use last_n to control batch size.",
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
        ),
         types.Tool(
        name="list_users",
        description="List all users",
        inputSchema={
            "type": "object",
            "properties": {
                "page_number": {"type": "integer", "description": "The page number to return."},
                "page_size": {"type": "integer", "description": "The number of users to return per page."}
            },
            "required": ["page_number", "page_size"],
            "additionalProperties": False
        }
    ),
    types.Tool(
        name="get_user_data",
        description="Get data for a specific user",
        inputSchema={
            "type": "object",
            "properties": {"user_id": {"type": "string", "description": "The user's unique identifier."}},
            "required": ["user_id"],
            "additionalProperties": False
        }
    )
]