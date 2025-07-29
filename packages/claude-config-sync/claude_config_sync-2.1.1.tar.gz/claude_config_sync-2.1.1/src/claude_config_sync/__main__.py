"""Main entry point for the Claude Config Sync MCP server."""

import asyncio
import logging
import sys
import traceback
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .server import create_server

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point for the MCP server."""
    try:
        logger.info("Initializing Claude Config Sync MCP server...")
        
        server = create_server()
        logger.info("Server created successfully")
        
        logger.info("Starting stdio server...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio streams established")
            
            initialization_options = server.create_initialization_options()
            logger.info(f"Initialization options: {initialization_options}")
            
            logger.info("Starting server.run()...")
            await server.run(read_stream, write_stream, initialization_options)
            
    except Exception as e:
        logger.error(f"Error in main(): {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def cli_main() -> None:
    """CLI entry point that runs the async main function."""
    try:
        logger.info("Starting Claude Config Sync MCP Server")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()