import time, threading, requests, logging

logger = logging.getLogger("CloudDelta")

# Stubbed for FOSS/Zero-Cost - connects to public pricing APIs
PRICING_SOURCES = [
    "https://api.tensordock.com/api/v0/client/deploy/host_list", 
    # Add Vast.ai / RunPod public endpoints here
]

class CloudDeltaEngine:
    def __init__(self):
        self.best_prices = {"gpu": [], "cpu": [], "last_updated": None}
        self.last_check = 0
        self.lock = threading.Lock()
    
    def get_pricing(self):
        """Get cached pricing data, refresh if stale"""
        with self.lock:
            # Lazy check: only update if requested > 15 mins ago
            if time.time() - self.last_check > 900:
                self._refresh_prices()
            return self.best_prices

    def _refresh_prices(self):
        """Refresh pricing data from external APIs"""
        # In a real deploy, this queries real APIs. 
        # For v1.0.1, we simulate the logic to prove the architecture.
        try:
            logger.info("🔄 Refreshing cloud pricing data...")
            
            # Mocking the aggregation logic
            # In production, this would query TensorDock, Vast.ai, RunPod APIs
            self.best_prices = {
                "gpu": [
                    {"provider": "TensorDock", "gpu": "RTX 3090", "price_per_hour": 0.18, "region": "US-Central", "vram_gb": 24},
                    {"provider": "Vast.ai", "gpu": "RTX 4090", "price_per_hour": 0.35, "region": "EU-West", "vram_gb": 24},
                    {"provider": "RunPod", "gpu": "A100 40GB", "price_per_hour": 0.89, "region": "US-East", "vram_gb": 40}
                ],
                "cpu": [
                    {"provider": "TensorDock", "cores": 16, "ram_gb": 64, "price_per_hour": 0.08, "region": "US-Central"},
                    {"provider": "Vast.ai", "cores": 32, "ram_gb": 128, "price_per_hour": 0.15, "region": "EU-West"}
                ],
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
            
            self.last_check = time.time()
            logger.info(f"✓ Cloud pricing updated: {len(self.best_prices['gpu'])} GPU options found")
            
        except Exception as e:
            logger.error(f"Cloud Delta Failed: {e}")
            self.best_prices["error"] = str(e)

    def get_cheapest_gpu(self, min_vram_gb=8):
        """Get the cheapest GPU option meeting minimum VRAM requirement"""
        pricing = self.get_pricing()
        if "error" in pricing:
            return None
        
        eligible = [g for g in pricing["gpu"] if g.get("vram_gb", 0) >= min_vram_gb]
        if not eligible:
            return None
        
        return min(eligible, key=lambda x: x["price_per_hour"])
