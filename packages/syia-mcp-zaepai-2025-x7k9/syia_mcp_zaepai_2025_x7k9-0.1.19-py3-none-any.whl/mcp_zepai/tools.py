from typing import List, Dict, Optional, Any, Sequence, Union
from zep_cloud.client import Zep
import mcp.types as types
from mcp_zepai.tool_schema import ZEP_SEARCH_TOOLS
from mcp_zepai.constants import ZEP_API_KEY
from mcp_zepai import mcp, logger

# Initialize Zep client only when needed, with proper error handling
def get_zep_client():
    """Get Zep client instance with proper error handling"""
    if not ZEP_API_KEY:
        raise ValueError("ZEP_API_KEY is not configured. Please set the ZEP_API_KEY environment variable.")
    return Zep(api_key=ZEP_API_KEY)

def validate_user_or_group_id(user_id: Optional[str], group_id: Optional[str]):
    """Validate that at least one of user_id or group_id is provided"""
    if not user_id and not group_id:
        raise ValueError("Either user_id or group_id must be provided")

def register_tools():
    @mcp.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return ZEP_SEARCH_TOOLS

    @mcp.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        try:
            if name == "search_graph_nodes":
                return await search_graph_nodes(arguments)
            elif name == "search_graph_edges":
                return await search_graph_edges(arguments)
            elif name == "search_graph_episodes":
                return await search_graph_episodes(arguments)
            elif name == "get_node_data":
                return await get_node_data(arguments)
            elif name == "get_node_edges":
                return await get_node_edges(arguments)
            elif name == "get_node_episodes":
                return await get_node_episodes(arguments)
            elif name == "get_edge_data":
                return await get_edge_data(arguments)
            elif name == "get_episode_data":
                return await get_episode_data(arguments)
            elif name == "get_user_episodes":
                return await get_user_episodes(arguments)
            elif name == "get_group_episodes":
                return await get_group_episodes(arguments)
            elif name == "get_nodes_and_edges_by_episode":
                return await get_nodes_and_edges_by_episode(arguments)
            elif name == "list_entity_types":
                return await list_entity_types(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            logger.error(f"Error in handle_call_tool: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        

async def search_graph_nodes(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Search within the graph nodes
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
            
        query = arguments.get("query")
        user_id = arguments.get("user_id")
        group_id = arguments.get("group_id")
        scope = "nodes"
        
        zep_client = get_zep_client()

        params = {
            "query": query,
            "scope": scope
        }
        if user_id:
            params["user_id"] = user_id
        if group_id:
            params["group_id"] = group_id

        results = zep_client.graph.search(**params)

        return [types.TextContent(type="text", text=str(results.nodes))]
    except Exception as e:
        logger.error(f"Error in search_graph_nodes: {e}")
        return [types.TextContent(type="text", text=f"Error in search_graph_nodes: {str(e)}")]


async def search_graph_edges(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Search within the graph edges
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        query = arguments.get("query")
        user_id = arguments.get("user_id")
        group_id = arguments.get("group_id")
        scope = "edges"
        
        zep_client = get_zep_client()

        params = {
            "query": query,
            "scope": scope
        }
        if user_id:
            params["user_id"] = user_id
        if group_id:
            params["group_id"] = group_id

        results = zep_client.graph.search(**params)

        return [types.TextContent(type="text", text=str(results.edges))]
    except Exception as e:
        logger.error(f"Error in search_graph_edges: {e}")
        return [types.TextContent(type="text", text=f"Error in search_graph_edges: {str(e)}")]
    



async def search_graph_episodes(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Search within the graph nodes and edges
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
            
        query = arguments.get("query")
        user_id = arguments.get("user_id")
        group_id = arguments.get("group_id")
        scope = "episodes"
        
        zep_client = get_zep_client()

        params = {
            "query": query,
            "scope": scope
        }
        if user_id:
            params["user_id"] = user_id
        if group_id:
            params["group_id"] = group_id

        results = zep_client.graph.search(**params)

        return [types.TextContent(type="text", text=str(results.episodes))]
    except Exception as e:  
        logger.error(f"Error in search_graph_episodes: {e}")
        return [types.TextContent(type="text", text=f"Error in search_graph_episodes: {str(e)}")]
    


# node tools:

async def get_node_data(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get complete data for a specific node including its connections
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        node_id = arguments.get("node_id")
        
        if not node_id:
            raise ValueError("node_id parameter is required")
        
        zep_client = get_zep_client()
        node = zep_client.graph.node.get(node_id)
        
        return [types.TextContent(type="text", text=str(node))]
    except Exception as e:
        logger.error(f"Error in get_node_data: {e}")
        return [types.TextContent(type="text", text=f"Error in get_node_data: {str(e)}")]

async def get_node_edges(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get edges for a specific node
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        node_id = arguments.get("node_id")
        
        if not node_id:
            raise ValueError("node_id parameter is required")
        
        zep_client = get_zep_client()   
        node = zep_client.graph.node.get_edges(node_id)
        
        return [types.TextContent(type="text", text=str(node))]
    except Exception as e:
        logger.error(f"Error in get_node_edges: {e}")
        return [types.TextContent(type="text", text=f"Error in get_node_edges: {str(e)}")]

async def get_node_episodes(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]: 
    """
    Get episodes for a specific node
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        node_id = arguments.get("node_id")
        
        if not node_id:
            raise ValueError("node_id parameter is required")
        
        zep_client = get_zep_client()
        node = zep_client.graph.node.get_episodes(node_id)
        
        return [types.TextContent(type="text", text=str(node))]
    except Exception as e:
        logger.error(f"Error in get_node_episodes: {e}")
        return [types.TextContent(type="text", text=f"Error in get_node_episodes: {str(e)}")]
    
# edge tools:

async def get_edge_data(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get data for a specific edge
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        edge_id = arguments.get("edge_id")
        
        if not edge_id:
            raise ValueError("edge_id parameter is required")
            

        zep_client = get_zep_client()
        edge = zep_client.graph.edge.get(edge_id)
        
        return [types.TextContent(type="text", text=str(edge))]
    except Exception as e:
        logger.error(f"Error in get_edge_data: {e}")
        return [types.TextContent(type="text", text=f"Error in get_edge_data: {str(e)}")]
    

# episode tools:

async def get_episode_data(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get data for a specific episode
    """
    try:    
        if not arguments:
            raise ValueError("Arguments are required")
        
        episode_id = arguments.get("episode_id")
        
        if not episode_id:
            raise ValueError("episode_id parameter is required")
        
        zep_client = get_zep_client()
        episode = zep_client.graph.episode.get(episode_id)
        
        return [types.TextContent(type="text", text=str(episode))]
    except Exception as e:
        logger.error(f"Error in get_episode_data: {e}")
        return [types.TextContent(type="text", text=f"Error in get_episode_data: {str(e)}")]
    
    
async def get_user_episodes(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get episodes for a specific user
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        user_id = arguments.get("user_id")
        last_n = arguments.get("last_n", 10)
        
        if not user_id:
            raise ValueError("user_id parameter is required")

        zep_client = get_zep_client()

        episodes = zep_client.graph.episode.get_by_user_id(user_id, last_n)
        
        return [types.TextContent(type="text", text=str(episodes))]
    except Exception as e:
        logger.error(f"Error in get_user_episodes: {e}")
        return [types.TextContent(type="text", text=f"Error in get_user_episodes: {str(e)}")]
    
async def get_group_episodes(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get episodes for a specific group
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        group_id = arguments.get("group_id")
        last_n = arguments.get("last_n", 10)
        
        if not group_id:
            raise ValueError("group_id parameter is required")
        
        zep_client = get_zep_client()
        episodes = zep_client.graph.episode.get_by_group_id(group_id, last_n)
        
        return [types.TextContent(type="text", text=str(episodes))]
    except Exception as e:
        logger.error(f"Error in get_group_episodes: {e}")
        return [types.TextContent(type="text", text=f"Error in get_group_episodes: {str(e)}")]
    
async def get_nodes_and_edges_by_episode(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Get nodes and edges for a specific episode
    """
    try:
        if not arguments:
            raise ValueError("Arguments are required")
        
        episode_id = arguments.get("episode_id")
        
        if not episode_id:
            raise ValueError("episode_id parameter is required")
        
        zep_client = get_zep_client()
        nodes_and_edges = zep_client.graph.episode.get_nodes_and_edges(episode_id)  

        return [types.TextContent(type="text", text=str(nodes_and_edges))]
    except Exception as e:
        logger.error(f"Error in get_nodes_and_edges_by_episode: {e}")
        return [types.TextContent(type="text", text=f"Error in get_nodes_and_edges_by_episode: {str(e)}")]
    

# schema tools:

async def list_entity_types(arguments: dict) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
    """
    Retrieve all available entity and edge types and their schemas
    """
    try:
        zep_client = get_zep_client()
        entity_types = zep_client.graph.list_entity_types()

        return [types.TextContent(type="text", text=str(entity_types))]
    except Exception as e:
        logger.error(f"Error in list_entity_types: {e}")
        return [types.TextContent(type="text", text=f"Error in list_entity_types: {str(e)}")]
