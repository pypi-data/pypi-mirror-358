import os
import argparse
from dotenv import load_dotenv
from mcp_zepai import logger

load_dotenv()


def get_config():
    parser = argparse.ArgumentParser(description="MCP ZepAI Configuration")
    
    # Zep configuration arguments
    parser.add_argument(
        "--zep-api-key",
        default=None,
        help="Zep server API key. Will use environment variable ZEP_API_KEY if not provided.",
    )
    
    args = parser.parse_args()

    # === Zep Configuration ===
    zep_api_key = args.zep_api_key or os.getenv("ZEP_API_KEY")
    logger.info(f"Final ZEP_API_KEY: {'Set' if zep_api_key else 'Not set'}")

    return zep_api_key
# Get configuration values for all services
ZEP_API_KEY = get_config()


# Zep optional validation
if not ZEP_API_KEY:
    logger.warning("Zep API key not provided. Zep functionality will be disabled.")




# Export values for use in other modules
__all__ = [
    "ZEP_API_KEY"
]

