"""
MCP ZepAI package initialization
"""

from mcp.server import Server
import logging
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = Server("mcp_zepai")

# Define server configuration
def get_server_config():
    return InitializationOptions(
        server_name="mcp-zepai",
        server_version="1.0.0",
        capabilities=mcp.get_capabilities(
            notification_options=NotificationOptions(resources_changed=True),
            experimental_capabilities={},
        ),
    )

__all__ = [
    'mcp',
    'get_server_config',
    'logger'
]