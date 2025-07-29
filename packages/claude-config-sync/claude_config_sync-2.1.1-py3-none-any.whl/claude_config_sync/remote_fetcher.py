"""Remote config fetcher for Digital Ocean integration."""

import json
import logging
import os
from typing import Any, Dict, Optional

import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)


class RemoteFetcher:
    """Fetches remote configuration from Digital Ocean."""

    def __init__(self):
        """Initialize the remote fetcher."""
        self.session = requests.Session()
        self.session.timeout = 30

    async def fetch_config(self) -> Optional[Dict[str, Any]]:
        """Fetch configuration from remote source."""
        remote_url = os.getenv("REMOTE_CONFIG_URL")
        if not remote_url:
            logger.error("REMOTE_CONFIG_URL environment variable not set")
            return None

        if "digitaloceanspaces.com" in remote_url or "spaces" in remote_url.lower():
            return await self._fetch_from_do_spaces(remote_url)
        else:
            return await self._fetch_from_url(remote_url)

    async def _fetch_from_do_spaces(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch config from Digital Ocean Spaces."""
        try:
            access_key = os.getenv("DO_SPACES_KEY")
            secret_key = os.getenv("DO_SPACES_SECRET")
            region = os.getenv("DO_REGION", "nyc3")

            if not access_key or not secret_key:
                logger.error("Digital Ocean Spaces credentials not provided")
                return None

            endpoint_url = f"https://{region}.digitaloceanspaces.com"
            
            s3_client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name=region
            )

            bucket_name, key = self._parse_spaces_url(url)
            if not bucket_name or not key:
                logger.error("Could not parse Digital Ocean Spaces URL")
                return None

            logger.info(f"Fetching from DO Spaces - Bucket: {bucket_name}, Key: {key}, Region: {region}")
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            content = response['Body'].read()
            
            config = json.loads(content.decode('utf-8'))
            logger.info("Successfully fetched config from Digital Ocean Spaces")
            return config

        except (ClientError, BotoCoreError) as e:
            logger.error(f"Digital Ocean Spaces error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in remote config: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch from Digital Ocean Spaces: {e}")
            return None

    async def _fetch_from_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Fetch config from a direct URL."""
        try:
            headers = {}
            
            # Note: DO_ACCESS_TOKEN is for Digital Ocean API, not for Spaces
            # For public URLs or if Spaces is configured with public read access,
            # no authentication headers are needed
            
            logger.info(f"Fetching config from URL: {url}")
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            config = response.json()
            logger.info("Successfully fetched config from URL")
            return config

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in remote config: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to fetch from URL: {e}")
            return None

    def _parse_spaces_url(self, url: str) -> tuple[Optional[str], Optional[str]]:
        """Parse Digital Ocean Spaces URL to extract bucket and key."""
        try:
            if "digitaloceanspaces.com" not in url:
                return None, None

            # URL format: https://bucket-name.region.digitaloceanspaces.com/key/path
            # Remove protocol
            url_without_protocol = url.replace("https://", "").replace("http://", "")
            
            # Split on first "/" to separate domain from path
            if "/" not in url_without_protocol:
                return None, None
                
            domain_part, path_part = url_without_protocol.split("/", 1)
            
            # Extract bucket name from domain (first part before first dot)
            domain_parts = domain_part.split(".")
            if len(domain_parts) < 3:  # Should be bucket.region.digitaloceanspaces.com
                return None, None
                
            bucket_name = domain_parts[0]
            key = path_part
            
            logger.debug(f"Parsed Spaces URL - Bucket: {bucket_name}, Key: {key}")
            return bucket_name, key
        except Exception as e:
            logger.error(f"Error parsing Spaces URL: {e}")
            return None, None

    def validate_remote_config(self, config: Dict[str, Any]) -> bool:
        """Validate the structure of remote config."""
        try:
            if not isinstance(config, dict):
                logger.error("Remote config is not a dictionary")
                return False

            if "mcpServers" not in config:
                logger.error("Remote config missing 'mcpServers' key")
                return False

            mcp_servers = config["mcpServers"]
            if not isinstance(mcp_servers, dict):
                logger.error("Remote config 'mcpServers' is not a dictionary")
                return False

            for server_name, server_config in mcp_servers.items():
                if not isinstance(server_config, dict):
                    logger.error(f"Server config for '{server_name}' is not a dictionary")
                    return False
                
                if "command" not in server_config:
                    logger.error(f"Server '{server_name}' missing 'command' field")
                    return False

            logger.info("Remote config validation passed")
            return True

        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return False