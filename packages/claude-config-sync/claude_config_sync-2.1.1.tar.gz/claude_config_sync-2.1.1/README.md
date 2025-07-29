# Claude Config Sync

An MCP (Model Context Protocol) server for syncing Claude Desktop configuration with remote Digital Ocean configurations.

## Features

- **Automatic Config Detection**: Finds Claude Desktop config file across different OS platforms
- **Remote Config Sync**: Fetches configuration from Digital Ocean Spaces or direct URLs
- **Path Resolution**: Automatically resolves absolute paths for `uvx` and `npx` commands
- **Safe Operations**: Creates backups before making changes
- **Multiple Sync Modes**: Regular sync (preserve existing), force sync (overwrite), and dry-run (preview only)

## Installation

Install using uvx:

```bash
uvx install claude-config-sync
```

## Configuration

Add the MCP server to your Claude Desktop config:

```json
{
  "mcpServers": {
    "claude-config-sync": {
      "command": "uvx",
      "args": ["claude-config-sync"],
      "env": {
        "DO_SPACES_KEY": "your-spaces-access-key-id",
        "DO_SPACES_SECRET": "your-spaces-secret-key",
        "REMOTE_CONFIG_URL": "https://your-space.digitaloceanspaces.com/config.json",
        "DO_REGION": "nyc3"
      }
    }
  }
}
```

### Environment Variables

- `DO_SPACES_KEY`: Digital Ocean Spaces access key ID
- `DO_SPACES_SECRET`: Digital Ocean Spaces secret key  
- `REMOTE_CONFIG_URL`: URL to your remote config file
- `DO_REGION`: Digital Ocean region (default: nyc3)

**Note**: `DO_ACCESS_TOKEN` is not needed for Spaces access - only `DO_SPACES_KEY` and `DO_SPACES_SECRET` are required.

## Available Tools

### `sync_config`
Adds new MCP servers from remote config while preserving existing local servers.

**Parameters:**
- `backup` (boolean, default: true): Create backup before syncing

### `force_sync_config`
Overwrites existing servers with remote versions and adds new ones.

**Parameters:**
- `backup` (boolean, default: true): Create backup before syncing

### `dry_run_sync`
Previews changes that would be made during sync without applying them.

### `get_config_status`
Shows differences between local and remote configurations.

## Usage Examples

1. **Sync new servers only (preserve existing)**:
   ```
   Use the sync_config tool
   ```

2. **Force sync all servers**:
   ```
   Use the force_sync_config tool
   ```

3. **Preview changes**:
   ```
   Use the dry_run_sync tool
   ```

4. **Check status**:
   ```
   Use the get_config_status tool
   ```

## Remote Config Format

Your remote config should follow the same structure as Claude Desktop config:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "package-name"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

## Security

- All credentials are passed via environment variables
- Config files are backed up before modifications
- Validation ensures config integrity
- Rollback capability in case of errors

## Development

```bash
# Clone the repository
git clone https://github.com/example/claude-config-sync.git
cd claude-config-sync

# Install dependencies
pip install -e .

# Run the server
python -m claude_config_sync
```

## License

MIT License