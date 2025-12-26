"""
Universal Connection Library Manager
Manages three symbiotic connection types: API Keys, Webhooks, and MCP Servers
"""
import os, json, time, logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger("ConnectionLibrary")

CONFIG_DIR = Path("/app/config")
API_LIBRARY = CONFIG_DIR / "api_library.json"
WEBHOOK_LIBRARY = CONFIG_DIR / "webhook_library.json"
MCP_LIBRARY = CONFIG_DIR / "mcp_library.json"

class ConnectionType(str, Enum):
    API = "api"
    WEBHOOK = "webhook"
    MCP = "mcp"

class ConnectionLibrary:
    """Manages all three connection libraries"""
    
    def __init__(self):
        self.libraries = {
            ConnectionType.API: API_LIBRARY,
            ConnectionType.WEBHOOK: WEBHOOK_LIBRARY,
            ConnectionType.MCP: MCP_LIBRARY
        }
        self._ensure_libraries_exist()
    
    def _ensure_libraries_exist(self):
        """Initialize library files if they don't exist"""
        CONFIG_DIR.mkdir(exist_ok=True)
        
        # API Library Template
        if not API_LIBRARY.exists():
            template = {
                "connections": {
                    "openai": {
                        "name": "OpenAI",
                        "base_url": "https://api.openai.com/v1",
                        "auth_type": "bearer",
                        "api_key_env": "OPENAI_API_KEY",
                        "models": ["gpt-4", "gpt-3.5-turbo"],
                        "capabilities": ["chat", "completion", "embedding"],
                        "enabled": True,
                        "added_at": time.time()
                    },
                    "anthropic": {
                        "name": "Anthropic",
                        "base_url": "https://api.anthropic.com/v1",
                        "auth_type": "api_key",
                        "api_key_env": "ANTHROPIC_API_KEY",
                        "models": ["claude-3-5-sonnet-20241022"],
                        "capabilities": ["chat", "completion"],
                        "enabled": True,
                        "added_at": time.time()
                    }
                }
            }
            API_LIBRARY.write_text(json.dumps(template, indent=4))
            logger.info("✓ API Library initialized")
        
        # Webhook Library Template
        if not WEBHOOK_LIBRARY.exists():
            template = {
                "webhooks": {
                    "example_webhook": {
                        "name": "Example Webhook",
                        "url": "https://hooks.example.com/webhook",
                        "method": "POST",
                        "headers": {},
                        "events": ["completion", "error"],
                        "enabled": False,
                        "added_at": time.time()
                    }
                }
            }
            WEBHOOK_LIBRARY.write_text(json.dumps(template, indent=4))
            logger.info("✓ Webhook Library initialized")
        
        # MCP Library Template
        if not MCP_LIBRARY.exists():
            template = {
                "servers": {
                    "filesystem": {
                        "name": "Filesystem MCP",
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                        "capabilities": ["read", "write", "list"],
                        "enabled": False,
                        "added_at": time.time()
                    }
                }
            }
            MCP_LIBRARY.write_text(json.dumps(template, indent=4))
            logger.info("✓ MCP Library initialized")
    
    def _load_library(self, conn_type: ConnectionType) -> Dict:
        """Load a specific library"""
        library_path = self.libraries[conn_type]
        if library_path.exists():
            with open(library_path) as f:
                return json.load(f)
        return {}
    
    def _save_library(self, conn_type: ConnectionType, data: Dict):
        """Save a specific library"""
        library_path = self.libraries[conn_type]
        with open(library_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    # ===== API LIBRARY =====
    
    def add_api_connection(self, conn_id: str, config: Dict) -> bool:
        """Add or update an API connection"""
        try:
            library = self._load_library(ConnectionType.API)
            if "connections" not in library:
                library["connections"] = {}
            
            config["added_at"] = config.get("added_at", time.time())
            config["enabled"] = config.get("enabled", True)
            library["connections"][conn_id] = config
            
            self._save_library(ConnectionType.API, library)
            logger.info(f"➕ API connection added: {conn_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add API connection: {e}")
            return False
    
    def remove_api_connection(self, conn_id: str) -> bool:
        """Remove an API connection"""
        try:
            library = self._load_library(ConnectionType.API)
            if "connections" in library and conn_id in library["connections"]:
                del library["connections"][conn_id]
                self._save_library(ConnectionType.API, library)
                logger.info(f"➖ API connection removed: {conn_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove API connection: {e}")
            return False
    
    def list_api_connections(self, enabled_only: bool = False) -> Dict:
        """List all API connections"""
        library = self._load_library(ConnectionType.API)
        connections = library.get("connections", {})
        if enabled_only:
            return {k: v for k, v in connections.items() if v.get("enabled", True)}
        return connections
    
    # ===== WEBHOOK LIBRARY =====
    
    def add_webhook(self, webhook_id: str, config: Dict) -> bool:
        """Add or update a webhook"""
        try:
            library = self._load_library(ConnectionType.WEBHOOK)
            if "webhooks" not in library:
                library["webhooks"] = {}
            
            config["added_at"] = config.get("added_at", time.time())
            config["enabled"] = config.get("enabled", True)
            library["webhooks"][webhook_id] = config
            
            self._save_library(ConnectionType.WEBHOOK, library)
            logger.info(f"➕ Webhook added: {webhook_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add webhook: {e}")
            return False
    
    def remove_webhook(self, webhook_id: str) -> bool:
        """Remove a webhook"""
        try:
            library = self._load_library(ConnectionType.WEBHOOK)
            if "webhooks" in library and webhook_id in library["webhooks"]:
                del library["webhooks"][webhook_id]
                self._save_library(ConnectionType.WEBHOOK, library)
                logger.info(f"➖ Webhook removed: {webhook_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove webhook: {e}")
            return False
    
    def list_webhooks(self, enabled_only: bool = False) -> Dict:
        """List all webhooks"""
        library = self._load_library(ConnectionType.WEBHOOK)
        webhooks = library.get("webhooks", {})
        if enabled_only:
            return {k: v for k, v in webhooks.items() if v.get("enabled", True)}
        return webhooks
    
    def trigger_webhook(self, webhook_id: str, payload: Dict) -> bool:
        """Trigger a webhook with payload"""
        import httpx
        try:
            webhooks = self.list_webhooks(enabled_only=True)
            if webhook_id not in webhooks:
                logger.warning(f"Webhook not found or disabled: {webhook_id}")
                return False
            
            webhook = webhooks[webhook_id]
            method = webhook.get("method", "POST").upper()
            url = webhook["url"]
            headers = webhook.get("headers", {})
            
            with httpx.Client(timeout=30) as client:
                if method == "POST":
                    resp = client.post(url, json=payload, headers=headers)
                elif method == "GET":
                    resp = client.get(url, params=payload, headers=headers)
                else:
                    resp = client.request(method, url, json=payload, headers=headers)
                
                logger.info(f"🔔 Webhook triggered: {webhook_id} -> {resp.status_code}")
                return resp.status_code < 400
        except Exception as e:
            logger.error(f"Webhook trigger failed: {e}")
            return False
    
    # ===== MCP LIBRARY =====
    
    def add_mcp_server(self, server_id: str, config: Dict) -> bool:
        """Add or update an MCP server"""
        try:
            library = self._load_library(ConnectionType.MCP)
            if "servers" not in library:
                library["servers"] = {}
            
            config["added_at"] = config.get("added_at", time.time())
            config["enabled"] = config.get("enabled", True)
            library["servers"][server_id] = config
            
            self._save_library(ConnectionType.MCP, library)
            logger.info(f"➕ MCP server added: {server_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add MCP server: {e}")
            return False
    
    def remove_mcp_server(self, server_id: str) -> bool:
        """Remove an MCP server"""
        try:
            library = self._load_library(ConnectionType.MCP)
            if "servers" in library and server_id in library["servers"]:
                del library["servers"][server_id]
                self._save_library(ConnectionType.MCP, library)
                logger.info(f"➖ MCP server removed: {server_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove MCP server: {e}")
            return False
    
    def list_mcp_servers(self, enabled_only: bool = False) -> Dict:
        """List all MCP servers"""
        library = self._load_library(ConnectionType.MCP)
        servers = library.get("servers", {})
        if enabled_only:
            return {k: v for k, v in servers.items() if v.get("enabled", True)}
        return servers
    
    # ===== UNIVERSAL OPERATIONS =====
    
    def get_all_connections(self) -> Dict:
        """Get all connections from all three libraries"""
        return {
            "api": self.list_api_connections(),
            "webhooks": self.list_webhooks(),
            "mcp_servers": self.list_mcp_servers()
        }
    
    def search_connections(self, query: str) -> Dict:
        """Search across all libraries"""
        query_lower = query.lower()
        results = {"api": {}, "webhooks": {}, "mcp_servers": {}}
        
        # Search API connections
        for conn_id, conn in self.list_api_connections().items():
            if query_lower in conn_id.lower() or query_lower in conn.get("name", "").lower():
                results["api"][conn_id] = conn
        
        # Search webhooks
        for webhook_id, webhook in self.list_webhooks().items():
            if query_lower in webhook_id.lower() or query_lower in webhook.get("name", "").lower():
                results["webhooks"][webhook_id] = webhook
        
        # Search MCP servers
        for server_id, server in self.list_mcp_servers().items():
            if query_lower in server_id.lower() or query_lower in server.get("name", "").lower():
                results["mcp_servers"][server_id] = server
        
        return results
    
    def get_stats(self) -> Dict:
        """Get statistics about all libraries"""
        api_conns = self.list_api_connections()
        webhooks = self.list_webhooks()
        mcp_servers = self.list_mcp_servers()
        
        return {
            "api_connections": {
                "total": len(api_conns),
                "enabled": len([c for c in api_conns.values() if c.get("enabled", True)])
            },
            "webhooks": {
                "total": len(webhooks),
                "enabled": len([w for w in webhooks.values() if w.get("enabled", True)])
            },
            "mcp_servers": {
                "total": len(mcp_servers),
                "enabled": len([s for s in mcp_servers.values() if s.get("enabled", True)])
            }
        }
