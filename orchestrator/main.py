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
from vault_manager import vault_manager
from ghost_daemon import init_ghost_daemon, activate_ghost_mode, deactivate_ghost_mode, get_ghost_status, start_daemon
from seat_router import init_seat_router, get_router
from model_discovery import get_discovery
from cost_optimizer import get_optimizer
from context_camera import get_context_camera, process_camera_command

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VertexOrchestrator")

app = FastAPI(title="Vertex Orchestrator v1.3.0", version="1.3.0")
manager = VertexProviderManager()
memory = VertexMemoryEngine()
cloud_delta = CloudDeltaEngine()
lifecycle = LifecycleMonitor(enabled=os.getenv("DISABLE_LIFECYCLE", "false").lower() != "true")
connection_lib = ConnectionLibrary()
universal_adapter = UniversalAdapter()

# Initialize Ghost Mode and Seat Router
init_ghost_daemon(lifecycle)
init_seat_router(lifecycle)
router = get_router()
discovery = get_discovery()

# Start Ghost Mode daemon if enabled
if os.getenv("ENABLE_GHOST_MODE", "false").lower() == "true":
    start_daemon()
    logger.info("👻 Ghost Mode daemon started")

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
        "version": "1.1.1",
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
        "version": "1.1.1",
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


# ===== VAULTWARDEN INTEGRATION (v1.1.1) =====

class VaultAuthRequest(BaseModel):
    email: str
    master_password: str

class VaultCipherRequest(BaseModel):
    name: str
    username: Optional[str] = None
    password: Optional[str] = None
    uri: Optional[str] = None
    notes: Optional[str] = None
    auto_generate_password: bool = False

class VaultAPIKeyRequest(BaseModel):
    service_name: str
    api_key: str
    api_url: Optional[str] = None
    notes: Optional[str] = None

class VaultDatabaseRequest(BaseModel):
    db_name: str
    db_host: str
    db_user: str
    db_password: Optional[str] = None
    db_port: int = 5432

@app.post("/v1/vault/auth")
async def vault_authenticate(req: VaultAuthRequest):
    """Authenticate with Vaultwarden"""
    lifecycle.touch()
    try:
        success = await vault_manager.authenticate(req.email, req.master_password)
        if success:
            return {"status": "authenticated", "message": "Successfully authenticated with Vaultwarden"}
        else:
            raise HTTPException(401, detail="Authentication failed")
    except Exception as e:
        logger.error(f"Vault auth error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/vault/cipher")
async def vault_create_cipher(req: VaultCipherRequest):
    """Create a new cipher in Vaultwarden"""
    lifecycle.touch()
    try:
        result = await vault_manager.create_cipher(
            name=req.name,
            username=req.username,
            password=req.password,
            uri=req.uri,
            notes=req.notes,
            auto_generate_password=req.auto_generate_password
        )
        return result
    except Exception as e:
        logger.error(f"Cipher creation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/vault/ciphers")
async def vault_list_ciphers():
    """List all ciphers"""
    lifecycle.touch()
    try:
        ciphers = await vault_manager.list_ciphers()
        return {"ciphers": ciphers, "count": len(ciphers)}
    except Exception as e:
        logger.error(f"Cipher list error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/vault/cipher/{cipher_id}")
async def vault_get_cipher(cipher_id: str):
    """Get a specific cipher by ID"""
    lifecycle.touch()
    try:
        cipher = await vault_manager.get_cipher(cipher_id)
        if cipher:
            return cipher
        else:
            raise HTTPException(404, detail="Cipher not found")
    except Exception as e:
        logger.error(f"Cipher retrieval error: {e}")
        raise HTTPException(500, detail=str(e))

@app.delete("/v1/vault/cipher/{cipher_id}")
async def vault_delete_cipher(cipher_id: str):
    """Delete a cipher by ID"""
    lifecycle.touch()
    try:
        success = await vault_manager.delete_cipher(cipher_id)
        if success:
            return {"status": "deleted", "cipher_id": cipher_id}
        else:
            raise HTTPException(500, detail="Deletion failed")
    except Exception as e:
        logger.error(f"Cipher deletion error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/vault/search")
async def vault_search_ciphers(q: str):
    """Search ciphers by name or username"""
    lifecycle.touch()
    try:
        results = await vault_manager.search_ciphers(q)
        return {"results": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Cipher search error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/vault/api-key")
async def vault_create_api_key(req: VaultAPIKeyRequest):
    """Create a cipher for API key storage"""
    lifecycle.touch()
    try:
        result = await vault_manager.create_api_key_cipher(
            service_name=req.service_name,
            api_key=req.api_key,
            api_url=req.api_url,
            notes=req.notes
        )
        return result
    except Exception as e:
        logger.error(f"API key cipher creation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/vault/database")
async def vault_create_database(req: VaultDatabaseRequest):
    """Create a cipher for database credentials with auto-generated password"""
    lifecycle.touch()
    try:
        result = await vault_manager.create_database_cipher(
            db_name=req.db_name,
            db_host=req.db_host,
            db_user=req.db_user,
            db_password=req.db_password,
            db_port=req.db_port
        )
        return result
    except Exception as e:
        logger.error(f"Database cipher creation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/vault/generate-password")
async def vault_generate_password(length: int = 32, include_symbols: bool = True):
    """Generate a secure random password"""
    lifecycle.touch()
    try:
        password = vault_manager.generate_password(length, include_symbols)
        return {"password": password, "length": len(password)}
    except Exception as e:
        logger.error(f"Password generation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/vault/generate-2fa")
async def vault_generate_2fa(account_name: str, issuer: str = "Vertex Genesis"):
    """Generate a 2FA secret and TOTP URI"""
    lifecycle.touch()
    try:
        secret = vault_manager.generate_2fa_secret()
        uri = vault_manager.generate_totp_uri(secret, account_name, issuer)
        return {
            "secret": secret,
            "uri": uri,
            "account_name": account_name,
            "issuer": issuer,
            "instructions": "Scan the QR code generated from the URI in your authenticator app"
        }
    except Exception as e:
        logger.error(f"2FA generation error: {e}")
        raise HTTPException(500, detail=str(e))


# ========== GHOST MODE ENDPOINTS ==========

@app.post("/v1/ghost/activate")
async def ghost_activate():
    """Activate Ghost Mode (listening state)"""
    lifecycle.touch()
    try:
        activate_ghost_mode()
        return {"status": "activated", "message": "Ghost Mode is now listening"}
    except Exception as e:
        logger.error(f"Ghost activation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/ghost/deactivate")
async def ghost_deactivate():
    """Deactivate Ghost Mode"""
    lifecycle.touch()
    try:
        deactivate_ghost_mode()
        return {"status": "deactivated", "message": "Ghost Mode deactivated"}
    except Exception as e:
        logger.error(f"Ghost deactivation error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/ghost/status")
async def ghost_status():
    """Get Ghost Mode status"""
    lifecycle.touch()
    try:
        status = get_ghost_status()
        return status
    except Exception as e:
        logger.error(f"Ghost status error: {e}")
        raise HTTPException(500, detail=str(e))

# ========== SEAT ROUTER ENDPOINTS ==========

class SeatAssignRequest(BaseModel):
    seat_id: int
    task_description: str

@app.post("/v1/seats/assign")
async def seat_assign(req: SeatAssignRequest):
    """Assign optimal model to seat based on task"""
    lifecycle.touch()
    try:
        result = router.assign(req.seat_id, req.task_description)
        return result
    except Exception as e:
        logger.error(f"Seat assignment error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/seats/status")
async def seats_status():
    """Get status of all seats"""
    lifecycle.touch()
    try:
        status = router.get_all_seats_status()
        return {"seats": status}
    except Exception as e:
        logger.error(f"Seats status error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/seats/{seat_id}")
async def seat_status(seat_id: int):
    """Get status of specific seat"""
    lifecycle.touch()
    try:
        status = router.get_seat_status(seat_id)
        return status
    except Exception as e:
        logger.error(f"Seat status error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/seats/{seat_id}/unload")
async def seat_unload(seat_id: int):
    """Unload model from seat"""
    lifecycle.touch()
    try:
        router.unload_seat(seat_id)
        return {"status": "unloaded", "seat_id": seat_id}
    except Exception as e:
        logger.error(f"Seat unload error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/seats/models")
async def seats_list_models():
    """List all indexed models"""
    lifecycle.touch()
    try:
        models = router.list_indexed_models()
        return {"models": models, "count": len(models)}
    except Exception as e:
        logger.error(f"List models error: {e}")
        raise HTTPException(500, detail=str(e))

# ========== MODEL DISCOVERY ENDPOINTS ==========

@app.post("/v1/discovery/scan")
async def discovery_scan(force: bool = False):
    """Trigger model discovery scan"""
    lifecycle.touch()
    try:
        models = discovery.discover_models(force=force)
        return {"models": models, "count": len(models)}
    except Exception as e:
        logger.error(f"Discovery scan error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/discovery/pricing")
async def discovery_pricing():
    """Get cloud spot pricing"""
    lifecycle.touch()
    try:
        pricing = discovery.discover_pricing()
        return {"pricing": pricing, "count": len(pricing)}
    except Exception as e:
        logger.error(f"Pricing discovery error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/discovery/optimal")
async def discovery_optimal(task_type: str = "general"):
    """Get optimal model and pricing configuration"""
    lifecycle.touch()
    try:
        config = discovery.get_optimal_config(task_type=task_type)
        return config
    except Exception as e:
        logger.error(f"Optimal config error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/discovery/cache")
async def discovery_cache():
    """Get cached discovery data"""
    lifecycle.touch()
    try:
        cache = discovery.load_discovery_cache()
        return cache
    except Exception as e:
        logger.error(f"Cache load error: {e}")
        raise HTTPException(500, detail=str(e))

# ========== COST OPTIMIZER ENDPOINTS ==========

@app.get("/v1/cost/statistics")
async def cost_statistics():
    """Get cost optimization statistics"""
    lifecycle.touch()
    try:
        optimizer = get_optimizer()
        stats = optimizer.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Cost statistics error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/cost/suggestions")
async def cost_suggestions():
    """Get cost optimization suggestions"""
    lifecycle.touch()
    try:
        optimizer = get_optimizer()
        suggestions = optimizer.suggest_optimizations()
        return {"suggestions": suggestions, "count": len(suggestions)}
    except Exception as e:
        logger.error(f"Cost suggestions error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/cost/reset")
async def cost_reset():
    """Reset cost statistics"""
    lifecycle.touch()
    try:
        optimizer = get_optimizer()
        optimizer.reset_statistics()
        return {"status": "reset", "message": "Cost statistics reset successfully"}
    except Exception as e:
        logger.error(f"Cost reset error: {e}")
        raise HTTPException(500, detail=str(e))

# ========== CONTEXT CAMERA ENDPOINTS ==========

@app.post("/v1/camera/process")
async def camera_process(voice_input: str):
    """Process camera command from voice input"""
    lifecycle.touch()
    try:
        result = process_camera_command(voice_input)
        return result
    except Exception as e:
        logger.error(f"Camera process error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/v1/camera/status")
async def camera_status():
    """Get camera status"""
    lifecycle.touch()
    try:
        camera = get_context_camera()
        status = camera.get_status()
        return status
    except Exception as e:
        logger.error(f"Camera status error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/camera/deactivate")
async def camera_deactivate():
    """Deactivate camera"""
    lifecycle.touch()
    try:
        camera = get_context_camera()
        camera.deactivate_camera()
        return {"status": "deactivated", "message": "Camera deactivated successfully"}
    except Exception as e:
        logger.error(f"Camera deactivate error: {e}")
        raise HTTPException(500, detail=str(e))

# ========== VAULT-CONNECTION INTEGRATION ==========

@app.post("/v1/connections/{conn_id}/store-credentials")
async def store_connection_credentials(conn_id: str, vault_entry_name: str):
    """Store connection credentials in Vaultwarden"""
    lifecycle.touch()
    try:
        # Get connection from library
        conn = connection_lib.get_connection(conn_id)
        if not conn:
            raise HTTPException(404, detail="Connection not found")
        
        # Store in vault
        vault_result = vault_manager.create_cipher(
            name=vault_entry_name,
            username=conn_id,
            password=conn.get('api_key_value', ''),
            notes=f"Auto-stored from connection library: {conn.get('name', conn_id)}"
        )
        
        return {
            "status": "stored",
            "connection_id": conn_id,
            "vault_entry": vault_entry_name,
            "vault_result": vault_result
        }
    except Exception as e:
        logger.error(f"Store credentials error: {e}")
        raise HTTPException(500, detail=str(e))

@app.post("/v1/connections/auto-store-all")
async def auto_store_all_credentials():
    """Auto-store all connection credentials in Vaultwarden"""
    lifecycle.touch()
    try:
        connections = connection_lib.list_connections()
        stored = []
        
        for conn in connections:
            conn_id = conn.get('conn_id')
            if conn.get('api_key_value'):
                try:
                    vault_result = vault_manager.create_cipher(
                        name=f"vertex_{conn_id}",
                        username=conn_id,
                        password=conn['api_key_value'],
                        notes=f"Auto-stored: {conn.get('name', conn_id)}"
                    )
                    stored.append(conn_id)
                except Exception as e:
                    logger.warning(f"Failed to store {conn_id}: {e}")
        
        return {
            "status": "completed",
            "stored_count": len(stored),
            "stored_connections": stored
        }
    except Exception as e:
        logger.error(f"Auto-store error: {e}")
        raise HTTPException(500, detail=str(e))
