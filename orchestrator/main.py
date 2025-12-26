from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import psutil, os, logging
from dynamic_manager import VertexProviderManager
from memory import VertexMemoryEngine
from cloud_delta import CloudDeltaEngine
from lifecycle import LifecycleMonitor
from connection_library import ConnectionLibrary, ConnectionType
from universal_adapter import UniversalAdapter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VertexOrchestrator")

app = FastAPI(title="Vertex Orchestrator v1.1.0", version="1.1.0")
manager = VertexProviderManager()
memory = VertexMemoryEngine()
cloud_delta = CloudDeltaEngine()
lifecycle = LifecycleMonitor(enabled=os.getenv("DISABLE_LIFECYCLE", "false").lower() != "true")
connection_lib = ConnectionLibrary()
universal_adapter = UniversalAdapter()

# ===== MODELS =====

class Message(BaseModel):
    role: str
    content: str

class Request(BaseModel):
    provider: str
    model: Optional[str] = None
    messages: List[Message]
    temperature: float = 0.7
    use_memory: bool = True

class ProviderConfig(BaseModel):
    name: str
    base_url: str
    auth_header: Optional[str] = "Authorization"
    auth_prefix: Optional[str] = "Bearer"
    api_key_env: Optional[str] = None
    api_key_value: Optional[str] = None
    models: List[str] = ["default"]

class APIConnectionConfig(BaseModel):
    conn_id: str
    name: str
    base_url: str
    auth_type: str = "bearer"  # bearer, api_key, custom
    api_key_env: Optional[str] = None
    api_key_value: Optional[str] = None
    auth_header: Optional[str] = None
    auth_prefix: Optional[str] = None
    models: List[str] = []
    capabilities: List[str] = []
    headers: Dict[str, str] = {}
    enabled: bool = True

class WebhookConfig(BaseModel):
    webhook_id: str
    name: str
    url: str
    method: str = "POST"
    headers: Dict[str, str] = {}
    events: List[str] = []
    enabled: bool = True

class MCPServerConfig(BaseModel):
    server_id: str
    name: str
    command: str
    args: List[str] = []
    capabilities: List[str] = []
    enabled: bool = True

class ConnectionConfirmation(BaseModel):
    """AI confirmation request for new connections"""
    connection_type: str  # api, webhook, mcp
    user_input: str  # Raw voice/text input
    parsed_config: Dict[str, Any]  # AI-parsed configuration
    confirmation_needed: List[str]  # Fields needing confirmation

# ===== LEGACY PROVIDER ENDPOINTS (v1.0.1 compatibility) =====

@app.post("/v1/providers")
async def register_provider(config: ProviderConfig):
    """Register a new AI provider at runtime (legacy)"""
    lifecycle.touch()
    try:
        config_dict = config.dict(exclude={"name"})
        manager.register_provider(config.name, config_dict)
        return {"status": "registered", "provider": config.name, "models": config.models}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/v1/providers")
async def list_providers():
    """List all available providers (legacy)"""
    lifecycle.touch()
    return {"providers": manager.list_providers()}

# ===== UNIVERSAL CONNECTION LIBRARY ENDPOINTS =====

@app.post("/v1/connections/api")
async def add_api_connection(config: APIConnectionConfig):
    """Add a new API connection to the library"""
    lifecycle.touch()
    try:
        conn_config = config.dict(exclude={"conn_id"})
        success = connection_lib.add_api_connection(config.conn_id, conn_config)
        if success:
            return {
                "status": "added",
                "connection_id": config.conn_id,
                "type": "api",
                "name": config.name
            }
        else:
            raise HTTPException(500, detail="Failed to add connection")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.delete("/v1/connections/api/{conn_id}")
async def remove_api_connection(conn_id: str):
    """Remove an API connection"""
    lifecycle.touch()
    success = connection_lib.remove_api_connection(conn_id)
    if success:
        return {"status": "removed", "connection_id": conn_id}
    else:
        raise HTTPException(404, detail="Connection not found")

@app.get("/v1/connections/api")
async def list_api_connections(enabled_only: bool = False):
    """List all API connections"""
    lifecycle.touch()
    return connection_lib.list_api_connections(enabled_only=enabled_only)

@app.post("/v1/connections/webhook")
async def add_webhook(config: WebhookConfig):
    """Add a new webhook to the library"""
    lifecycle.touch()
    try:
        webhook_config = config.dict(exclude={"webhook_id"})
        success = connection_lib.add_webhook(config.webhook_id, webhook_config)
        if success:
            return {
                "status": "added",
                "webhook_id": config.webhook_id,
                "type": "webhook",
                "name": config.name
            }
        else:
            raise HTTPException(500, detail="Failed to add webhook")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.delete("/v1/connections/webhook/{webhook_id}")
async def remove_webhook(webhook_id: str):
    """Remove a webhook"""
    lifecycle.touch()
    success = connection_lib.remove_webhook(webhook_id)
    if success:
        return {"status": "removed", "webhook_id": webhook_id}
    else:
        raise HTTPException(404, detail="Webhook not found")

@app.get("/v1/connections/webhook")
async def list_webhooks(enabled_only: bool = False):
    """List all webhooks"""
    lifecycle.touch()
    return connection_lib.list_webhooks(enabled_only=enabled_only)

@app.post("/v1/connections/mcp")
async def add_mcp_server(config: MCPServerConfig):
    """Add a new MCP server to the library"""
    lifecycle.touch()
    try:
        server_config = config.dict(exclude={"server_id"})
        success = connection_lib.add_mcp_server(config.server_id, server_config)
        if success:
            return {
                "status": "added",
                "server_id": config.server_id,
                "type": "mcp",
                "name": config.name
            }
        else:
            raise HTTPException(500, detail="Failed to add MCP server")
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.delete("/v1/connections/mcp/{server_id}")
async def remove_mcp_server(server_id: str):
    """Remove an MCP server"""
    lifecycle.touch()
    success = connection_lib.remove_mcp_server(server_id)
    if success:
        return {"status": "removed", "server_id": server_id}
    else:
        raise HTTPException(404, detail="MCP server not found")

@app.get("/v1/connections/mcp")
async def list_mcp_servers(enabled_only: bool = False):
    """List all MCP servers"""
    lifecycle.touch()
    return connection_lib.list_mcp_servers(enabled_only=enabled_only)

@app.get("/v1/connections/all")
async def get_all_connections():
    """Get all connections from all three libraries"""
    lifecycle.touch()
    return connection_lib.get_all_connections()

@app.get("/v1/connections/search")
async def search_connections(q: str):
    """Search across all connection libraries"""
    lifecycle.touch()
    return connection_lib.search_connections(q)

@app.get("/v1/connections/stats")
async def get_connection_stats():
    """Get statistics about all connection libraries"""
    lifecycle.touch()
    return connection_lib.get_stats()

@app.post("/v1/connections/confirm")
async def confirm_connection(confirmation: ConnectionConfirmation):
    """AI-assisted confirmation for new connections"""
    lifecycle.touch()
    # This endpoint is called by the Studio to confirm parsed connection details
    # The AI will ask user to confirm spelling, URLs, etc.
    return {
        "status": "confirmed",
        "connection_type": confirmation.connection_type,
        "parsed_config": confirmation.parsed_config,
        "ready_to_add": True
    }

# ===== CLOUD PRICING ENDPOINTS =====

@app.get("/v1/cloud/pricing")
async def get_cloud_pricing():
    """Get current cloud spot pricing data"""
    lifecycle.touch()
    return cloud_delta.get_pricing()

@app.get("/v1/cloud/cheapest")
async def get_cheapest_gpu(min_vram: int = 8):
    """Get the cheapest GPU option meeting minimum VRAM requirement"""
    lifecycle.touch()
    cheapest = cloud_delta.get_cheapest_gpu(min_vram_gb=min_vram)
    if cheapest:
        return cheapest
    else:
        raise HTTPException(404, detail="No GPU options found meeting requirements")

# ===== CHAT COMPLETION ENDPOINT =====

@app.post("/v1/chat/completions")
async def completions(req: Request, background_tasks: BackgroundTasks):
    """Main chat completion endpoint with memory integration"""
    lifecycle.touch()
    try:
        user_query = req.messages[-1].content
        system_prompt = next((m.content for m in req.messages if m.role == "system"), "You are a helpful assistant.")
        
        # 1. Recall from memory
        memory_context = ""
        if req.use_memory:
            memory_context = await memory.recall(user_query)
        
        full_system = f"{system_prompt}\n\nRELEVANT MEMORY:\n{memory_context}" if memory_context else system_prompt
        user_messages = [m.dict() for m in req.messages if m.role != "system"]
        
        # 2. Try universal adapter first, fallback to legacy manager
        try:
            messages_for_api = [{"role": "system", "content": full_system}] + user_messages
            ai_text = universal_adapter.chat_completion(req.provider, messages_for_api, req.model, temperature=req.temperature)
        except:
            # Fallback to legacy provider manager
            client = manager.get_client(req.provider)
            
            if req.provider == "anthropic":
                resp = client.post("/messages", json={
                    "model": req.model or "claude-3-5-sonnet-20241022", 
                    "system": full_system, 
                    "messages": user_messages, 
                    "max_tokens": 4096
                })
                ai_text = resp.json()["content"][0]["text"]
            elif req.provider == "gemini":
                contents = [{"role": "user", "parts": [{"text": f"System: {full_system}\n\nUser: {m['content']}"}]} for m in user_messages]
                resp = client.post(f"/{req.model or 'gemini-1.5-pro'}:generateContent", json={"contents": contents})
                ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                resp = client.post("/chat/completions", json={
                    "model": req.model or "default",
                    "messages": [{"role": "system", "content": full_system}] + user_messages,
                    "temperature": req.temperature
                })
                ai_text = resp.json()["choices"][0]["message"]["content"]
            
            manager.mark_used(req.provider)
        
        # 3. Async Memorize
        if req.use_memory:
            background_tasks.add_task(memory.memorize, user_query, ai_text)
        
        # 4. Trigger webhooks
        background_tasks.add_task(
            universal_adapter.trigger_webhooks, 
            "completion", 
            {"provider": req.provider, "query": user_query, "response": ai_text}
        )
            
        return {
            "content": ai_text, 
            "provider": req.provider, 
            "memory_injected": bool(memory_context),
            "model": req.model
        }
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(500, detail=str(e))

# ===== HEALTH & STATUS =====

@app.get("/health")
def health():
    """Health check endpoint with system status"""
    lifecycle.touch()
    return {
        "status": "online",
        "version": "1.1.0",
        "active_providers": list(manager.clients.keys()),
        "available_providers": manager.list_providers(),
        "connection_stats": connection_lib.get_stats(),
        "ram_mb": round(psutil.Process().memory_info().rss / 1024**2, 2),
        "idle_time_seconds": round(lifecycle.get_idle_time(), 2)
    }

@app.get("/")
def root():
    """Root endpoint"""
    lifecycle.touch()
    return {
        "name": "Vertex Orchestrator",
        "version": "1.1.0",
        "tagline": "Universal AI Connection Framework",
        "features": [
            "Runtime Provider Registration",
            "Universal API Connection Library",
            "Webhook Integration Library",
            "MCP Server Library",
            "Cloud Spot Pricing Discovery",
            "Self-Termination (Idle Suicide)",
            "Vector Memory with Qdrant",
            "Multi-Provider AI Integration"
        ],
        "libraries": {
            "api_connections": len(connection_lib.list_api_connections()),
            "webhooks": len(connection_lib.list_webhooks()),
            "mcp_servers": len(connection_lib.list_mcp_servers())
        }
    }
