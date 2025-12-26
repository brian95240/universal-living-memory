from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import psutil, os
from manager import VertexProviderManager
from memory import VertexMemoryEngine

app = FastAPI(title="Vertex Orchestrator")
manager = VertexProviderManager()
memory = VertexMemoryEngine()

class Message(BaseModel):
    role: str
    content: str

class Request(BaseModel):
    provider: str
    model: Optional[str] = None
    messages: List[Message]
    temperature: float = 0.7
    use_memory: bool = True

@app.post("/v1/chat/completions")
async def completions(req: Request, background_tasks: BackgroundTasks):
    try:
        user_query = req.messages[-1].content
        system_prompt = next((m.content for m in req.messages if m.role == "system"), "You are a helpful assistant.")
        
        # 1. Recall
        memory_context = ""
        if req.use_memory:
            memory_context = await memory.recall(user_query)
        
        full_system = f"{system_prompt}\n\nRELEVANT MEMORY:\n{memory_context}" if memory_context else system_prompt
        user_messages = [m.dict() for m in req.messages if m.role != "system"]
        
        # 2. Inference
        client = manager.get_client(req.provider)
        
        if req.provider == "anthropic":
            resp = client.post("/messages", json={
                "model": req.model, "system": full_system, "messages": user_messages, "max_tokens": 4096
            })
            ai_text = resp.json()["content"][0]["text"]
        elif req.provider == "gemini":
            # Gemini specific adapter
            contents = [{"role": "user", "parts": [{"text": f"System: {full_system}\n\nUser: {m['content']}"}]} for m in user_messages]
            resp = client.post("", json={"contents": contents})
            ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # OpenAI/Grok/Local
            resp = client.post("/chat/completions", json={
                "model": req.model or "default",
                "messages": [{"role": "system", "content": full_system}] + user_messages
            })
            ai_text = resp.json()["choices"][0]["message"]["content"]
            
        manager.mark_used(req.provider)
        
        # 3. Async Memorize
        if req.use_memory:
            background_tasks.add_task(memory.memorize, user_query, ai_text)
            
        return {"content": ai_text, "provider": req.provider, "memory_injected": bool(memory_context)}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/health")
def health():
    return {
        "status": "online",
        "active_providers": list(manager.clients.keys()),
        "ram_mb": psutil.Process().memory_info().rss / 1024**2
    }
