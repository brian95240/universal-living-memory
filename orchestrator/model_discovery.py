"""
Model Discovery Engine - Universal Model Hunting
Vertex Genesis v1.2.0

Merges delta_scan (model hunting) with cloud_delta (spot pricing).
Runs once per day or on demand, discovers optimal models and pricing.
"""

import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path('./agents')
CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Timestamp file
LAST_HUNT_FILE = CACHE_DIR / '.last_hunt'


class ModelDiscovery:
    """
    Universal model and pricing discovery engine.
    Hunts for optimal models and cloud spot pricing.
    """
    
    def __init__(self):
        self.last_hunt = self._read_last_hunt()
        self.hunt_interval = 86400  # 24 hours
        logger.info("🔍 ModelDiscovery initialized")
    
    def _read_last_hunt(self) -> float:
        """Read last hunt timestamp."""
        try:
            if LAST_HUNT_FILE.exists():
                return float(LAST_HUNT_FILE.read_text())
        except:
            pass
        return 0.0
    
    def _write_last_hunt(self, timestamp: float):
        """Write last hunt timestamp."""
        LAST_HUNT_FILE.write_text(str(timestamp))
    
    def should_hunt(self) -> bool:
        """Check if enough time has passed for new hunt."""
        now = time.time()
        return (now - self.last_hunt) >= self.hunt_interval
    
    def _pull_huggingface_trending(self) -> List[Dict[str, Any]]:
        """
        Pull trending models from HuggingFace.
        
        Returns:
            List of model dictionaries
        """
        models = []
        
        try:
            # Mock data for now - real implementation would scrape HF API
            models = [
                {
                    'id': 'mistralai/Mistral-7B-Instruct-v0.2',
                    'desc': 'fast code generation, quick reasoning, low RAM usage',
                    'source': 'huggingface',
                    'score': 0.95
                },
                {
                    'id': 'google/gemma-2-9b-it',
                    'desc': 'strong safety, low bias, great voice tone, instruction following',
                    'source': 'huggingface',
                    'score': 0.92
                },
                {
                    'id': 'meta-llama/Llama-3.2-11B-Vision-Instruct',
                    'desc': 'sees text, reads signs, OCR built-in, multimodal',
                    'source': 'huggingface',
                    'score': 0.90
                },
                {
                    'id': 'microsoft/phi-3-mini-4k-instruct',
                    'desc': 'tiny brain, offline scribe, zero network, embedded',
                    'source': 'huggingface',
                    'score': 0.88
                }
            ]
            
            logger.info(f"✅ Pulled {len(models)} models from HuggingFace")
        except Exception as e:
            logger.error(f"❌ HuggingFace pull error: {e}")
        
        return models
    
    def _pull_lmsys_leaderboard(self) -> List[Dict[str, Any]]:
        """
        Pull top models from LMSys Chatbot Arena leaderboard.
        
        Returns:
            List of model dictionaries
        """
        models = []
        
        try:
            # Mock data - real implementation would fetch from LMSys API
            models = [
                {
                    'id': 'gpt-4-turbo',
                    'desc': 'highest reasoning, complex tasks, expensive',
                    'source': 'lmsys',
                    'score': 0.98
                },
                {
                    'id': 'claude-3-opus',
                    'desc': 'creative writing, long context, safety focused',
                    'source': 'lmsys',
                    'score': 0.97
                },
                {
                    'id': 'gemini-pro-1.5',
                    'desc': 'multimodal, fast, good balance',
                    'source': 'lmsys',
                    'score': 0.94
                }
            ]
            
            logger.info(f"✅ Pulled {len(models)} models from LMSys")
        except Exception as e:
            logger.error(f"❌ LMSys pull error: {e}")
        
        return models
    
    def _pull_github_stars(self) -> List[Dict[str, Any]]:
        """
        Pull popular models from GitHub stars.
        
        Returns:
            List of model dictionaries
        """
        models = []
        
        try:
            # Mock data - real implementation would use GitHub API
            models = [
                {
                    'id': 'ollama/llama3',
                    'desc': 'local inference, privacy, no API keys',
                    'source': 'github',
                    'score': 0.89
                },
                {
                    'id': 'ggerganov/llama.cpp',
                    'desc': 'CPU inference, quantized, fast',
                    'source': 'github',
                    'score': 0.87
                }
            ]
            
            logger.info(f"✅ Pulled {len(models)} models from GitHub")
        except Exception as e:
            logger.error(f"❌ GitHub pull error: {e}")
        
        return models
    
    def _pull_cloud_pricing(self) -> List[Dict[str, Any]]:
        """
        Pull cloud GPU spot pricing.
        
        Returns:
            List of pricing dictionaries
        """
        pricing = []
        
        try:
            # Mock data - real implementation would fetch from cloud APIs
            pricing = [
                {
                    'provider': 'runpod',
                    'gpu': 'RTX 4090',
                    'price_per_hour': 0.34,
                    'availability': 'high'
                },
                {
                    'provider': 'vast.ai',
                    'gpu': 'A100',
                    'price_per_hour': 0.89,
                    'availability': 'medium'
                },
                {
                    'provider': 'lambda',
                    'gpu': 'H100',
                    'price_per_hour': 1.99,
                    'availability': 'low'
                }
            ]
            
            logger.info(f"✅ Pulled {len(pricing)} pricing options")
        except Exception as e:
            logger.error(f"❌ Cloud pricing pull error: {e}")
        
        return pricing
    
    def discover_models(self, force: bool = False) -> List[Dict[str, Any]]:
        """
        Discover models from all sources.
        
        Args:
            force: Force discovery even if recently hunted
        
        Returns:
            List of discovered models
        """
        now = time.time()
        
        # Check if should hunt
        if not force and not self.should_hunt():
            logger.info("🔍 Hunt skipped (too soon)")
            return []
        
        logger.info("🔍 Starting model discovery...")
        
        # Pull from all sources
        models = []
        models.extend(self._pull_huggingface_trending())
        models.extend(self._pull_lmsys_leaderboard())
        models.extend(self._pull_github_stars())
        
        # Update last hunt timestamp
        self.last_hunt = now
        self._write_last_hunt(now)
        
        logger.info(f"✅ Discovery complete: {len(models)} models found")
        
        return models
    
    def discover_pricing(self) -> List[Dict[str, Any]]:
        """
        Discover cloud spot pricing.
        
        Returns:
            List of pricing options
        """
        logger.info("💰 Starting pricing discovery...")
        pricing = self._pull_cloud_pricing()
        logger.info(f"✅ Pricing discovery complete: {len(pricing)} options found")
        return pricing
    
    def get_optimal_config(self, task_type: str = "general") -> Dict[str, Any]:
        """
        Get optimal model and pricing configuration for task type.
        
        Args:
            task_type: Type of task (general, code, vision, etc.)
        
        Returns:
            Optimal configuration dictionary
        """
        models = self.discover_models()
        pricing = self.discover_pricing()
        
        # Simple heuristic for now
        if task_type == "code":
            optimal_model = next((m for m in models if 'code' in m['desc']), models[0] if models else None)
        elif task_type == "vision":
            optimal_model = next((m for m in models if 'vision' in m['desc'] or 'OCR' in m['desc']), models[0] if models else None)
        else:
            optimal_model = models[0] if models else None
        
        optimal_pricing = min(pricing, key=lambda p: p['price_per_hour']) if pricing else None
        
        return {
            "model": optimal_model,
            "pricing": optimal_pricing,
            "task_type": task_type,
            "timestamp": time.time()
        }
    
    def save_discovery_cache(self, models: List[Dict[str, Any]], pricing: List[Dict[str, Any]]):
        """
        Save discovery results to cache.
        
        Args:
            models: List of models
            pricing: List of pricing options
        """
        cache_file = CACHE_DIR / 'discovery_cache.json'
        
        try:
            cache = {
                "timestamp": time.time(),
                "models": models,
                "pricing": pricing
            }
            cache_file.write_text(json.dumps(cache, indent=2))
            logger.info(f"💾 Discovery cache saved: {cache_file}")
        except Exception as e:
            logger.error(f"❌ Cache save error: {e}")
    
    def load_discovery_cache(self) -> Dict[str, Any]:
        """
        Load discovery results from cache.
        
        Returns:
            Cached discovery data
        """
        cache_file = CACHE_DIR / 'discovery_cache.json'
        
        try:
            if cache_file.exists():
                cache = json.loads(cache_file.read_text())
                logger.info(f"✅ Discovery cache loaded")
                return cache
        except Exception as e:
            logger.error(f"❌ Cache load error: {e}")
        
        return {"timestamp": 0, "models": [], "pricing": []}


# Singleton instance
_global_discovery: Optional[ModelDiscovery] = None


def get_discovery() -> ModelDiscovery:
    """Get or create global discovery instance."""
    global _global_discovery
    if _global_discovery is None:
        _global_discovery = ModelDiscovery()
    return _global_discovery


# Simple usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    discovery = ModelDiscovery()
    
    # Discover models
    models = discovery.discover_models(force=True)
    print(f"Discovered {len(models)} models")
    
    # Discover pricing
    pricing = discovery.discover_pricing()
    print(f"Discovered {len(pricing)} pricing options")
    
    # Get optimal config
    config = discovery.get_optimal_config(task_type="code")
    print(f"Optimal config: {config}")
    
    # Save cache
    discovery.save_discovery_cache(models, pricing)
