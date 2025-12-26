import os, json, time, gc, threading, logging, httpx
from pathlib import Path

COLLAPSE_TTL = 300
CONFIG_PATH = Path("/app/config/providers.json")
logger = logging.getLogger("DynamicManager")

class VertexProviderManager:
    def __init__(self):
        self.clients = {}
        self.last_used = {}
        self.lock = threading.Lock()
        self.config = self._load_config()

    def _load_config(self):
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH) as f: 
                return json.load(f).get("providers", {})
        return {}

    def reload_config(self):
        """Reload configuration from disk"""
        with self.lock:
            self.config = self._load_config()

    def list_providers(self):
        """Return list of available provider names"""
        return list(self.config.keys())

    def register_provider(self, name, config_dict):
        """Runtime Registration of new models"""
        with self.lock:
            # Load current config
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH) as f:
                    full_conf = json.load(f)
            else:
                full_conf = {"providers": {}}
            
            if "providers" not in full_conf:
                full_conf["providers"] = {}
            
            # Add new provider
            full_conf["providers"][name] = config_dict
            
            # Save to disk
            with open(CONFIG_PATH, 'w') as f:
                json.dump(full_conf, f, indent=4)
            
            # Update in-memory config
            self.config = full_conf["providers"]
            logger.info(f"➕ Registered Provider: {name}")
            return True

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
        if provider not in self.config:
            raise ValueError(f"Unknown provider: {provider}")
            
        logger.info(f"🔥 Hydrating {provider}")
        cfg = self.config[provider]
        headers = {"Content-Type": "application/json"}
        
        # Dynamic Auth
        if cfg.get("auth_header"):
            key = os.getenv(cfg.get("api_key_env", ""), "")
            # If key not in env, check if passed in config (for runtime adds)
            if not key: 
                key = cfg.get("api_key_value", "")
            
            prefix = f"{cfg.get('auth_prefix')} " if cfg.get("auth_prefix") else ""
            headers[cfg["auth_header"]] = f"{prefix}{key}".strip()

        return httpx.Client(base_url=cfg["base_url"], headers=headers, timeout=60)

    def mark_used(self, provider):
        with self.lock:
            self.last_used[provider] = time.time()
