"""
Universal Adapter - Dynamically connects to any AI model, tool, or platform
Supports API connections, webhooks, and MCP servers
"""
import os, json, logging, httpx
from typing import Dict, List, Optional, Any
from connection_library import ConnectionLibrary

logger = logging.getLogger("UniversalAdapter")

class UniversalAdapter:
    """Adapts to any AI provider or service dynamically"""
    
    def __init__(self):
        self.library = ConnectionLibrary()
        self.active_clients = {}
    
    def get_client(self, conn_id: str, conn_type: str = "api") -> Optional[httpx.Client]:
        """Get or create a client for a connection"""
        cache_key = f"{conn_type}:{conn_id}"
        
        if cache_key in self.active_clients:
            return self.active_clients[cache_key]
        
        if conn_type == "api":
            connections = self.library.list_api_connections(enabled_only=True)
            if conn_id not in connections:
                raise ValueError(f"API connection not found or disabled: {conn_id}")
            
            config = connections[conn_id]
            client = self._create_api_client(config)
            self.active_clients[cache_key] = client
            return client
        
        return None
    
    def _create_api_client(self, config: Dict) -> httpx.Client:
        """Create an HTTP client for an API connection"""
        base_url = config["base_url"]
        headers = {"Content-Type": "application/json"}
        
        # Handle different auth types
        auth_type = config.get("auth_type", "bearer")
        api_key_env = config.get("api_key_env")
        api_key_value = config.get("api_key_value")
        
        # Get API key from env or config
        api_key = None
        if api_key_env:
            api_key = os.getenv(api_key_env)
        if not api_key and api_key_value:
            api_key = api_key_value
        
        # Apply auth based on type
        if auth_type == "bearer" and api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        elif auth_type == "api_key" and api_key:
            headers["x-api-key"] = api_key
        elif auth_type == "custom":
            # Custom header from config
            auth_header = config.get("auth_header", "Authorization")
            auth_prefix = config.get("auth_prefix", "")
            if api_key:
                headers[auth_header] = f"{auth_prefix}{api_key}".strip()
        
        # Add any custom headers
        custom_headers = config.get("headers", {})
        headers.update(custom_headers)
        
        return httpx.Client(base_url=base_url, headers=headers, timeout=60)
    
    def call_api(self, conn_id: str, endpoint: str, method: str = "POST", 
                 data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """Universal API call to any connection"""
        try:
            client = self.get_client(conn_id, "api")
            
            if method.upper() == "POST":
                resp = client.post(endpoint, json=data)
            elif method.upper() == "GET":
                resp = client.get(endpoint, params=params)
            elif method.upper() == "PUT":
                resp = client.put(endpoint, json=data)
            elif method.upper() == "DELETE":
                resp = client.delete(endpoint)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"API call failed for {conn_id}: {e}")
            raise
    
    def chat_completion(self, conn_id: str, messages: List[Dict], 
                       model: Optional[str] = None, **kwargs) -> str:
        """Universal chat completion across different API formats"""
        connections = self.library.list_api_connections(enabled_only=True)
        if conn_id not in connections:
            raise ValueError(f"Connection not found: {conn_id}")
        
        config = connections[conn_id]
        
        # Detect API format based on base_url or explicit format
        api_format = config.get("api_format", self._detect_api_format(config["base_url"]))
        
        if api_format == "openai":
            return self._chat_openai_format(conn_id, messages, model, **kwargs)
        elif api_format == "anthropic":
            return self._chat_anthropic_format(conn_id, messages, model, **kwargs)
        elif api_format == "google":
            return self._chat_google_format(conn_id, messages, model, **kwargs)
        else:
            # Default to OpenAI-compatible format (most common)
            return self._chat_openai_format(conn_id, messages, model, **kwargs)
    
    def _detect_api_format(self, base_url: str) -> str:
        """Detect API format from base URL"""
        if "anthropic.com" in base_url:
            return "anthropic"
        elif "generativelanguage.googleapis.com" in base_url:
            return "google"
        elif "openai.com" in base_url or "x.ai" in base_url:
            return "openai"
        else:
            return "openai"  # Default to OpenAI-compatible
    
    def _chat_openai_format(self, conn_id: str, messages: List[Dict], 
                           model: Optional[str], **kwargs) -> str:
        """OpenAI-compatible chat format"""
        payload = {
            "model": model or "gpt-3.5-turbo",
            "messages": messages,
            **kwargs
        }
        resp = self.call_api(conn_id, "/chat/completions", "POST", payload)
        return resp["choices"][0]["message"]["content"]
    
    def _chat_anthropic_format(self, conn_id: str, messages: List[Dict], 
                              model: Optional[str], **kwargs) -> str:
        """Anthropic Claude format"""
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        
        payload = {
            "model": model or "claude-3-5-sonnet-20241022",
            "system": system,
            "messages": user_messages,
            "max_tokens": kwargs.get("max_tokens", 4096)
        }
        resp = self.call_api(conn_id, "/messages", "POST", payload)
        return resp["content"][0]["text"]
    
    def _chat_google_format(self, conn_id: str, messages: List[Dict], 
                           model: Optional[str], **kwargs) -> str:
        """Google Gemini format"""
        contents = []
        for msg in messages:
            contents.append({
                "role": "user" if msg["role"] in ["user", "system"] else "model",
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {"contents": contents}
        model_name = model or "gemini-1.5-pro"
        resp = self.call_api(conn_id, f"/{model_name}:generateContent", "POST", payload)
        return resp["candidates"][0]["content"]["parts"][0]["text"]
    
    def trigger_webhooks(self, event: str, payload: Dict):
        """Trigger all webhooks subscribed to an event"""
        webhooks = self.library.list_webhooks(enabled_only=True)
        triggered = []
        
        for webhook_id, webhook in webhooks.items():
            events = webhook.get("events", [])
            if event in events or "all" in events:
                success = self.library.trigger_webhook(webhook_id, payload)
                triggered.append({"webhook": webhook_id, "success": success})
        
        return triggered
    
    def list_available_models(self, conn_id: str) -> List[str]:
        """List available models for a connection"""
        connections = self.library.list_api_connections()
        if conn_id in connections:
            return connections[conn_id].get("models", [])
        return []
    
    def validate_connection(self, conn_id: str, conn_type: str = "api") -> Dict:
        """Validate a connection by testing it"""
        try:
            if conn_type == "api":
                client = self.get_client(conn_id, "api")
                # Try a simple request (health check or list models)
                resp = client.get("/")
                return {"valid": True, "status": resp.status_code}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def close_all_clients(self):
        """Close all active clients"""
        for client in self.active_clients.values():
            if isinstance(client, httpx.Client):
                client.close()
        self.active_clients.clear()
        logger.info("🧹 All clients closed")
