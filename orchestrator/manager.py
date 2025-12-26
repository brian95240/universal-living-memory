import os, json, time, gc, threading, logging, httpx
from pathlib import Path

COLLAPSE_TTL = 300
CONFIG_PATH = Path("/app/config/providers.json")
logger = logging.getLogger("VertexManager")

class VertexProviderManager:
    def __init__(self):
        self.clients = {}
        self.last_used = {}
        self.lock = threading.Lock()
        self.config = self._load_config()

    def _load_config(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f: return json.load(f).get("providers", {})
        return {}

    def get_client(self, provider):
        with self.lock:
            now = time.time()
            # Collapse Logic
            for p in list(self.clients.keys()):
                if now - self.last_used.get(p, 0) > COLLAPSE_TTL:
                    logger.info(f"❄️ Collapsing {p}")
                    self.clients[p].close()
                    del self.clients[p]
                    gc.collect()
            
            if provider not in self.clients:
                self.clients[provider] = self._hydrate(provider)
            self.last_used[provider] = now
            return self.clients[provider]

    def _hydrate(self, provider):
        logger.info(f"🔥 Hydrating {provider}")
        cfg = self.config.get(provider, {})
        key = os.getenv(cfg.get("api_key_env", ""), "")
        headers = {"Content-Type": "application/json"}
        
        if provider == "grok":
            return httpx.Client(base_url="https://api.x.ai/v1", headers={**headers, "Authorization": f"Bearer {key}"}, timeout=60)
        elif provider == "anthropic":
             return httpx.Client(base_url="https://api.anthropic.com/v1", headers={**headers, "x-api-key": key, "anthropic-version": "2023-06-01"}, timeout=60)
        elif provider == "gemini":
             return httpx.Client(base_url=f"https://generativelanguage.googleapis.com/v1beta/models/{cfg.get('model', 'gemini-1.5-pro')}:generateContent", params={"key": key}, headers=headers, timeout=60)
        # Local Fallback
        return httpx.Client(base_url="http://localhost:11434/v1", timeout=60)

    def mark_used(self, provider):
        with self.lock:
            self.last_used[provider] = time.time()
