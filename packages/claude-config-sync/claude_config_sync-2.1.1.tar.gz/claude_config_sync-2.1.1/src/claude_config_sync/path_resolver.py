"""Path resolver for finding absolute paths to commands."""

import logging
import os
import shutil
import subprocess
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PathResolver:
    """Resolves absolute paths for commands like uvx and npx."""

    def __init__(self):
        """Initialize the path resolver."""
        self._cached_paths = {}

    async def resolve_command_path(self, command: str) -> Optional[str]:
        """Resolve the absolute path for a command."""
        if command in self._cached_paths:
            return self._cached_paths[command]

        try:
            absolute_path = shutil.which(command)
            if absolute_path:
                # Resolve any symlinks to get the real path
                real_path = os.path.realpath(absolute_path)
                self._cached_paths[command] = real_path
                logger.debug(f"Resolved {command} to {real_path}")
                return real_path
            else:
                logger.warning(f"Could not find command: {command}")
                return None
        except Exception as e:
            logger.error(f"Error resolving path for {command}: {e}")
            return None

    async def resolve_all_mcp_commands(self) -> Dict[str, Optional[str]]:
        """Resolve paths for all common MCP commands."""
        commands = ["uvx", "npx", "uv", "node", "python", "python3"]
        resolved = {}
        
        for cmd in commands:
            resolved[cmd] = await self.resolve_command_path(cmd)
            
        return resolved

    async def check_command_availability(self, command: str) -> Tuple[bool, Optional[str]]:
        """Check if a command is available and return its path."""
        path = await self.resolve_command_path(command)
        return (path is not None, path)

    def expand_tilde_path(self, path: str) -> str:
        """Expand ~ in paths to absolute paths."""
        if path.startswith("~"):
            return os.path.expanduser(path)
        return path

    async def normalize_command_paths(self, config: Dict) -> Tuple[Dict, List[str]]:
        """Normalize all command paths in config and return issues found."""
        issues = []
        normalized_config = config.copy()
        
        if "mcpServers" not in normalized_config:
            return normalized_config, issues

        # Build a fallback map of existing working paths
        fallback_paths = await self._build_fallback_paths(config)

        for server_name, server_config in normalized_config["mcpServers"].items():
            if "command" not in server_config:
                continue
                
            current_command = server_config["command"]
            
            # Handle tilde expansion
            if current_command.startswith("~"):
                expanded_path = self.expand_tilde_path(current_command)
                if os.path.exists(expanded_path):
                    server_config["command"] = expanded_path
                    logger.info(f"Expanded {current_command} to {expanded_path} for {server_name}")
                    continue
                else:
                    issues.append(f"Server '{server_name}': Expanded path {expanded_path} does not exist")

            # Extract command name from path
            command_name = os.path.basename(current_command)
            
            # Skip if it's already an absolute path that exists
            if os.path.isabs(current_command) and os.path.exists(current_command):
                continue
                
            # Try to resolve the correct path using which
            correct_path = await self.resolve_command_path(command_name)
            
            # If which didn't find it, try the fallback from existing config
            if not correct_path and command_name in fallback_paths:
                fallback_path = fallback_paths[command_name]
                if os.path.exists(fallback_path):
                    correct_path = fallback_path
                    logger.info(f"Using fallback path for {command_name}: {fallback_path}")
            
            if correct_path:
                if current_command != correct_path:
                    server_config["command"] = correct_path
                    logger.info(f"Updated {server_name}: {current_command} -> {correct_path}")
            else:
                issues.append(f"Server '{server_name}': Command '{command_name}' not found on system or in existing config")

        return normalized_config, issues

    async def _build_fallback_paths(self, config: Dict) -> Dict[str, str]:
        """Build a map of command names to existing working paths in the config."""
        fallback_paths = {}
        
        if "mcpServers" not in config:
            return fallback_paths
            
        for _, server_config in config["mcpServers"].items():
            if "command" not in server_config:
                continue
                
            command_path = server_config["command"]
            
            # Expand tilde if present
            if command_path.startswith("~"):
                command_path = self.expand_tilde_path(command_path)
            
            # If it's an absolute path that exists, add to fallback map
            if os.path.isabs(command_path) and os.path.exists(command_path):
                command_name = os.path.basename(command_path)
                # Only add if we don't already have a fallback for this command
                if command_name not in fallback_paths:
                    fallback_paths[command_name] = command_path
                    logger.debug(f"Added fallback for {command_name}: {command_path}")
        
        return fallback_paths

    def clear_cache(self):
        """Clear the cached paths."""
        self._cached_paths.clear()