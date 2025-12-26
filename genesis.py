import psutil, platform, json, torch, subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
TARGET_VOLUME_LABEL = "Seagate"
FALLBACK_STORAGE = PROJECT_ROOT / "local_storage"
PROVIDERS_CONFIG = PROJECT_ROOT / "config" / "providers.json"

def get_specs():
    specs = {
        "os": platform.system(),
        "cpu": psutil.cpu_count(logical=False),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": {"count": 0, "name": "None", "vram": 0}
    }
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        specs["gpu"] = {"count": torch.cuda.device_count(), "name": p.name, "vram": round(p.total_memory / (1024**3), 2)}
    return specs

def find_storage(label):
    for p in psutil.disk_partitions():
        try:
            if label.lower() in p.mountpoint.lower(): return p.mountpoint
        except: continue
    return str(FALLBACK_STORAGE)

def gen_env(specs, storage):
    mem_limit = min(int(specs['ram_gb'] * 1024 * 0.4), 4096)
    env = f"PROJECT_ROOT={PROJECT_ROOT}\nEXTERNAL_STORAGE_PATH={storage}\nDB_MEM_LIMIT={mem_limit}m\nAI_WORKER_THREADS={max(2, specs['cpu']-2)}"
    (PROJECT_ROOT / ".env").write_text(env)
    print(f"[✓] .env generated. Storage: {storage}")

def init_config():
    if not PROVIDERS_CONFIG.exists():
        (PROJECT_ROOT / "config").mkdir(exist_ok=True)
        # Dynamic Schema: Defines HOW to connect, not just keys
        template = {
            "providers": {
                "grok": {
                    "base_url": "https://api.x.ai/v1",
                    "auth_header": "Authorization",
                    "auth_prefix": "Bearer",
                    "api_key_env": "GROK_API_KEY",
                    "models": ["grok-beta"]
                },
                "anthropic": {
                    "base_url": "https://api.anthropic.com/v1",
                    "auth_header": "x-api-key",
                    "auth_prefix": None,
                    "api_key_env": "ANTHROPIC_API_KEY",
                    "models": ["claude-3-5-sonnet-20241022"]
                },
                "gemini": {
                    "base_url": "https://generativelanguage.googleapis.com/v1beta",
                    "auth_header": None,
                    "api_key_env": "GEMINI_API_KEY",
                    "models": ["gemini-1.5-pro"]
                },
                "local": {
                    "base_url": "http://host.docker.internal:11434/v1",
                    "auth_header": None,
                    "models": ["llama3", "mistral"]
                }
            }
        }
        PROVIDERS_CONFIG.write_text(json.dumps(template, indent=4))
        print(f"[✓] providers.json initialized")

if __name__ == "__main__":
    print("[GENESIS v1.0.1] Initializing Hardware Discovery...")
    specs = get_specs()
    print(f"[INFO] Detected: {specs['cpu']} cores, {specs['ram_gb']}GB RAM, GPU: {specs['gpu']['name']}")
    storage = find_storage(TARGET_VOLUME_LABEL)
    if storage == str(FALLBACK_STORAGE): 
        FALLBACK_STORAGE.mkdir(exist_ok=True)
        print(f"[WARN] External storage not found. Using fallback: {FALLBACK_STORAGE}")
    gen_env(specs, storage)
    init_config()
    print("[✓] Genesis configuration complete!")
