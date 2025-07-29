"""Configuration manager for Claude Desktop config operations."""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .path_resolver import PathResolver

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages Claude Desktop configuration file operations."""

    def __init__(self):
        """Initialize the config manager."""
        self.path_resolver = PathResolver()
        self._config_path: Optional[Path] = None

    def _find_config_path(self) -> Optional[Path]:
        """Find the Claude Desktop config file path."""
        if self._config_path and self._config_path.exists():
            return self._config_path

        home = Path.home()
        possible_paths = [
            home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
            home / ".config" / "Claude" / "claude_desktop_config.json",
            home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json",
        ]

        for path in possible_paths:
            if path.exists():
                self._config_path = path
                logger.info(f"Found Claude config at: {path}")
                return path

        logger.error("Could not find Claude Desktop config file")
        return None

    async def load_local_config(self) -> Dict[str, Any]:
        """Load the local Claude Desktop configuration."""
        config_path = self._find_config_path()
        if not config_path:
            raise FileNotFoundError("Claude Desktop config file not found")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("Successfully loaded local config")
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise Exception(f"Failed to load config file: {e}")

    async def save_config(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """Save configuration to file with optional backup."""
        config_path = self._find_config_path()
        if not config_path:
            raise FileNotFoundError("Claude Desktop config file not found")

        try:
            if backup:
                await self._create_backup(config_path)

            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info("Successfully saved config")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    async def _create_backup(self, config_path: Path) -> Path:
        """Create a backup of the config file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config_path.parent / f"claude_desktop_config_backup_{timestamp}.json"
        
        shutil.copy2(config_path, backup_path)
        logger.info(f"Created backup at: {backup_path}")
        return backup_path

    async def sync_config(self, remote_config: Dict[str, Any], force: bool = False, backup: bool = True) -> Dict[str, Any]:
        """Sync local config with remote config."""
        try:
            local_config = await self.load_local_config()
            result = {
                "success": False,
                "added": [],
                "updated": [],
                "path_fixes": [],
                "issues": [],
                "error": None
            }

            if "mcpServers" not in local_config:
                local_config["mcpServers"] = {}

            remote_servers = remote_config.get("mcpServers", {})
            local_servers = local_config["mcpServers"]

            # Add/update servers from remote
            for server_name, server_config in remote_servers.items():
                processed_config = await self._process_server_config(server_config)
                
                if server_name not in local_servers:
                    local_servers[server_name] = processed_config
                    result["added"].append(server_name)
                    logger.info(f"Added new server: {server_name}")
                elif force:
                    local_servers[server_name] = processed_config
                    result["updated"].append(server_name)
                    logger.info(f"Updated server (forced): {server_name}")

            # Normalize all command paths in the config
            normalized_config, path_issues = await self.path_resolver.normalize_command_paths(local_config)
            
            # Track path fixes
            for server_name, server_config in normalized_config.get("mcpServers", {}).items():
                original_command = local_config.get("mcpServers", {}).get(server_name, {}).get("command")
                new_command = server_config.get("command")
                if original_command and new_command and original_command != new_command:
                    result["path_fixes"].append(f"{server_name}: {original_command} -> {new_command}")

            result["issues"] = path_issues
            
            await self.save_config(normalized_config, backup=backup)
            result["success"] = True
            return result

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            return {
                "success": False,
                "added": [],
                "updated": [],
                "path_fixes": [],
                "issues": [],
                "error": str(e)
            }

    async def preview_changes(self, remote_config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Preview what changes would be made during sync."""
        try:
            local_config = await self.load_local_config()
            local_servers = set(local_config.get("mcpServers", {}).keys())
            remote_servers = set(remote_config.get("mcpServers", {}).keys())

            new_servers = list(remote_servers - local_servers)
            updated_servers = list(local_servers & remote_servers)

            # Analyze path changes that would be made
            _, path_issues = await self.path_resolver.normalize_command_paths(local_config)
            
            # Check for potential path fixes
            path_fixes = []
            for server_name, server_config in local_config.get("mcpServers", {}).items():
                current_command = server_config.get("command", "")
                if current_command:
                    command_name = os.path.basename(current_command)
                    correct_path = await self.path_resolver.resolve_command_path(command_name)
                    if correct_path and current_command != correct_path:
                        path_fixes.append(f"{server_name}: {current_command} -> {correct_path}")

            return {
                "new_servers": new_servers,
                "updated_servers": updated_servers,
                "path_fixes": path_fixes,
                "issues": path_issues
            }
        except Exception as e:
            logger.error(f"Preview failed: {e}")
            raise

    async def _process_server_config(self, server_config: Dict[str, Any]) -> Dict[str, Any]:
        """Process server config to resolve absolute paths."""
        processed = server_config.copy()
        
        if "command" in processed:
            command = processed["command"]
            if command in ["uvx", "npx"]:
                absolute_path = await self.path_resolver.resolve_command_path(command)
                if absolute_path:
                    processed["command"] = absolute_path
                    logger.debug(f"Resolved {command} to {absolute_path}")

        return processed

    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate configuration structure."""
        try:
            if not isinstance(config, dict):
                return False, "Config must be a dictionary"

            if "mcpServers" in config:
                mcp_servers = config["mcpServers"]
                if not isinstance(mcp_servers, dict):
                    return False, "mcpServers must be a dictionary"

                for server_name, server_config in mcp_servers.items():
                    if not isinstance(server_config, dict):
                        return False, f"Server config for '{server_name}' must be a dictionary"
                    
                    if "command" not in server_config:
                        return False, f"Server '{server_name}' missing required 'command' field"

            return True, None
        except Exception as e:
            return False, f"Validation error: {str(e)}"