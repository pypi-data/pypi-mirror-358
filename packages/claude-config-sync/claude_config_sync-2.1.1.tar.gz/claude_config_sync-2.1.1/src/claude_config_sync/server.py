"""MCP server implementation for Claude Config Sync."""

import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from .config_manager import ConfigManager
from .remote_fetcher import RemoteFetcher

logger = logging.getLogger(__name__)


def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("claude-config-sync")
    config_manager = ConfigManager()
    remote_fetcher = RemoteFetcher()

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools."""
        return [
            Tool(
                name="sync_config",
                description="Sync Claude Desktop config with remote config. Adds new servers while preserving existing ones.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup": {
                            "type": "boolean",
                            "description": "Create backup before syncing (default: true)",
                            "default": True
                        }
                    }
                }
            ),
            Tool(
                name="force_sync_config", 
                description="Force sync Claude Desktop config with remote config. Overwrites existing servers with remote versions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "backup": {
                            "type": "boolean",
                            "description": "Create backup before syncing (default: true)",
                            "default": True
                        }
                    }
                }
            ),
            Tool(
                name="dry_run_sync",
                description="Preview changes that would be made during sync without applying them.",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="get_config_status",
                description="Show differences between local and remote configurations.",
                inputSchema={
                    "type": "object", 
                    "properties": {}
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls."""
        try:
            if name == "sync_config":
                return await handle_sync_config(arguments, force=False)
            elif name == "force_sync_config":
                return await handle_sync_config(arguments, force=True)
            elif name == "dry_run_sync":
                return await handle_dry_run_sync()
            elif name == "get_config_status":
                return await handle_config_status()
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_sync_config(arguments: Dict[str, Any], force: bool = False) -> List[TextContent]:
        """Handle sync config tool calls."""
        backup = arguments.get("backup", True)
        
        try:
            remote_config = await remote_fetcher.fetch_config()
            if not remote_config:
                return [TextContent(type="text", text="Failed to fetch remote config")]
            
            result = await config_manager.sync_config(remote_config, force=force, backup=backup)
            
            if result["success"]:
                message = f"Config sync {'(forced)' if force else ''} completed successfully!\n"
                message += f"Added {len(result['added'])} new servers"
                if result['updated']:
                    message += f", updated {len(result['updated'])} servers"
                if result['path_fixes']:
                    message += f", fixed {len(result['path_fixes'])} command paths"
                
                if result['added']:
                    message += f"\n\nNew servers: {', '.join(result['added'])}"
                if result['updated']:
                    message += f"\nUpdated servers: {', '.join(result['updated'])}"
                if result['path_fixes']:
                    message += f"\n\nPath fixes applied:"
                    for fix in result['path_fixes']:
                        message += f"\n  - {fix}"
                if result['issues']:
                    message += f"\n\nIssues found:"
                    for issue in result['issues']:
                        message += f"\n  ⚠️  {issue}"
                
                return [TextContent(type="text", text=message)]
            else:
                return [TextContent(type="text", text=f"Sync failed: {result['error']}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Sync error: {str(e)}")]

    async def handle_dry_run_sync() -> List[TextContent]:
        """Handle dry run sync tool calls."""
        try:
            remote_config = await remote_fetcher.fetch_config()
            if not remote_config:
                return [TextContent(type="text", text="Failed to fetch remote config")]
            
            changes = await config_manager.preview_changes(remote_config)
            
            has_changes = (changes["new_servers"] or changes["updated_servers"] or 
                          changes.get("path_fixes") or changes.get("issues"))
            
            if not has_changes:
                message = "No changes would be made - config is already in sync!\n"
                message += "✅ All servers are up to date\n"
                message += "✅ All command paths are correct"
                return [TextContent(type="text", text=message)]
            
            message = "Preview of changes that would be made:\n\n"
            
            if changes["new_servers"]:
                message += f"📥 New servers to be added ({len(changes['new_servers'])}):\n"
                for server in changes["new_servers"]:
                    message += f"  + {server}\n"
                message += "\n"
            
            if changes["updated_servers"]:
                message += f"🔄 Servers that would be updated ({len(changes['updated_servers'])}):\n"
                for server in changes["updated_servers"]:
                    message += f"  ~ {server}\n"
                message += "\n"
            
            if changes.get("path_fixes"):
                message += f"🔧 Command paths that would be fixed ({len(changes['path_fixes'])}):\n"
                for fix in changes["path_fixes"]:
                    message += f"  🛠️  {fix}\n"
                message += "\n"
            
            if changes.get("issues"):
                message += f"⚠️  Issues found ({len(changes['issues'])}):\n"
                for issue in changes["issues"]:
                    message += f"  ❌ {issue}\n"
            
            return [TextContent(type="text", text=message)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Dry run error: {str(e)}")]

    async def handle_config_status() -> List[TextContent]:
        """Handle config status tool calls."""
        try:
            local_config = await config_manager.load_local_config()
            remote_config = await remote_fetcher.fetch_config()
            
            if not remote_config:
                return [TextContent(type="text", text="Failed to fetch remote config")]
            
            local_servers = set(local_config.get("mcpServers", {}).keys())
            remote_servers = set(remote_config.get("mcpServers", {}).keys())
            
            new_in_remote = remote_servers - local_servers
            only_local = local_servers - remote_servers
            common = local_servers & remote_servers
            
            message = "Configuration Status:\n\n"
            message += f"Local servers: {len(local_servers)}\n"
            message += f"Remote servers: {len(remote_servers)}\n\n"
            
            if new_in_remote:
                message += f"Servers available in remote but not local ({len(new_in_remote)}):\n"
                for server in sorted(new_in_remote):
                    message += f"  - {server}\n"
                message += "\n"
            
            if only_local:
                message += f"Servers only in local config ({len(only_local)}):\n"
                for server in sorted(only_local):
                    message += f"  - {server}\n"
                message += "\n"
            
            if common:
                message += f"Common servers ({len(common)}):\n"
                for server in sorted(common):
                    message += f"  - {server}\n"
            
            return [TextContent(type="text", text=message)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Status error: {str(e)}")]

    return server