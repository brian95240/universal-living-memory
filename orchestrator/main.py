from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import psutil, os, logging
from dynamic_manager import VertexProviderManager
from memory import VertexMemoryEngine
from cloud_delta import CloudDeltaEngine
from lifecycle import LifecycleMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VertexOrchestrator")

app = FastAPI(title="Vertex Orchestrator v1.0.1", version="1.0.1")
manager = VertexProviderManager()
memory = VertexMemoryEngine()
cloud_delta = CloudDeltaEngine()
lifecycle = LifecycleMonitor(enabled=os.getenv("DISABLE_LIFECYCLE", "false").lower() != "true")

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

@app.post("/v1/providers")
async def register_provider(config: ProviderConfig):
    """Register a new AI provider at runtime"""
    lifecycle.touch()
    try:
        config_dict = config.dict(exclude={"name"})
        manager.register_provider(config.name, config_dict)
        return {"status": "registered", "provider": config.name, "models": config.models}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/v1/providers")
async def list_providers():
    """List all available providers"""
    lifecycle.touch()
    return {"providers": manager.list_providers()}

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
        
        # 2. Inference
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
            # Gemini specific adapter
            contents = [{"role": "user", "parts": [{"text": f"System: {full_system}\n\nUser: {m['content']}"}]} for m in user_messages]
            resp = client.post(f"/{req.model or 'gemini-1.5-pro'}:generateContent", json={"contents": contents})
            ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # OpenAI/Grok/Local compatible
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
            
        return {
            "content": ai_text, 
            "provider": req.provider, 
            "memory_injected": bool(memory_context),
            "model": req.model
        }
    except Exception as e:
        logger.error(f"Completion error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/health")
def health():
    """Health check endpoint with system status"""
    lifecycle.touch()
    return {
        "status": "online",
        "version": "1.0.1",
        "active_providers": list(manager.clients.keys()),
        "available_providers": manager.list_providers(),
        "ram_mb": round(psutil.Process().memory_info().rss / 1024**2, 2),
        "idle_time_seconds": round(lifecycle.get_idle_time(), 2)
    }

@app.get("/")
def root():
    """Root endpoint"""
    lifecycle.touch()
    return {
        "name": "Vertex Orchestrator",
        "version": "1.0.1",
        "features": [
            "Runtime Provider Registration",
            "Cloud Spot Pricing Discovery",
            "Self-Termination (Idle Suicide)",
            "Vector Memory with Qdrant",
            "Multi-Provider AI Integration"
        ]
    }
