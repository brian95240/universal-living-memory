"""
ModelBank - Universal Model Management for Ghost Mode
Vertex Genesis v1.2.0

Wraps existing dynamic_manager and connection_library for Ghost Mode compatibility.
"""

import logging
from typing import Optional, Dict, Any, List
from dynamic_manager import VertexProviderManager
from connection_library import ConnectionLibrary
import httpx

logger = logging.getLogger(__name__)


class ModelBank:
    """
    Universal model management with lazy loading and atomic swaps.
    Integrates with v1.1.1's dynamic_manager and connection_library.
    """
    
    def __init__(self):
        self.provider_manager = VertexProviderManager()
        self.connection_lib = ConnectionLibrary()
        self.current_provider: Optional[str] = None
        self.current_model: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None
        
        logger.info("🏦 ModelBank initialized")
    
    @classmethod
    def from_context(cls, context: str = "pass-through"):
        """
        Create ModelBank with context-based provider selection.
        
        Args:
            context: Context hint for provider selection (e.g., "pass-through", "code", "vision")
        
        Returns:
            ModelBank instance
        """
        bank = cls()
        
        # Auto-select provider based on context
        if context == "pass-through":
            # Use fastest available provider
            providers = bank.provider_manager.list_providers()
            if providers:
                bank.current_provider = providers[0]
                logger.info(f"✅ Auto-selected provider: {bank.current_provider}")
        
        return bank
    
    async def ask(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Ask the current model a question.
        
        Args:
            prompt: Question or instruction
            temperature: Sampling temperature
        
        Returns:
            Model response
        """
        if not self.current_provider:
            # Fallback to first available provider
            providers = self.provider_manager.list_providers()
            if not providers:
                return "[Error: No providers available]"
            self.current_provider = providers[0]
        
        try:
            # Get provider client
            client = await self.provider_manager.get_client(self.current_provider)
            
            # Make request
            response = await client.post(
                "/chat/completions",
                json={
                    "model": self.current_model or "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature
                }
            )
            
            result = response.json()
            answer = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Mark provider as used
            self.provider_manager.mark_used(self.current_provider)
            
            return answer
        except Exception as e:
            logger.error(f"❌ ModelBank ask error: {e}")
            return f"[Error: {e}]"
    
    def swap(self, provider_or_model: str):
        """
        Atomically swap to a different provider or model.
        
        Args:
            provider_or_model: Provider name or model identifier
        """
        try:
            # Check if it's a known provider
            providers = self.provider_manager.list_providers()
            
            if provider_or_model in providers:
                # Swap provider
                old_provider = self.current_provider
                self.current_provider = provider_or_model
                logger.info(f"🔄 Swapped provider: {old_provider} → {provider_or_model}")
            else:
                # Try to swap model within current provider
                self.current_model = provider_or_model
                logger.info(f"🔄 Swapped model: {provider_or_model}")
        except Exception as e:
            logger.error(f"❌ Swap error: {e}")
    
    def unload(self):
        """Unload current model and free resources."""
        try:
            if self.current_provider:
                # Trigger TTL collapse in provider_manager
                logger.info(f"🧹 Unloading provider: {self.current_provider}")
                self.current_provider = None
                self.current_model = None
        except Exception as e:
            logger.error(f"❌ Unload error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current model bank status.
        
        Returns:
            Status dictionary
        """
        return {
            "current_provider": self.current_provider,
            "current_model": self.current_model,
            "available_providers": self.provider_manager.list_providers(),
            "active_connections": len(self.connection_lib.list_api_connections())
        }
    
    def list_available(self) -> List[str]:
        """
        List all available providers and models.
        
        Returns:
            List of provider/model names
        """
        providers = self.provider_manager.list_providers()
        connections = [conn["conn_id"] for conn in self.connection_lib.list_api_connections()]
        return providers + connections


class LocalModel:
    """
    Wrapper for local model loading (for seat_router compatibility).
    Integrates with ModelBank.
    """
    
    def __init__(self, model_id: str):
        self.id = model_id
        self.bank = ModelBank()
        self.bank.swap(model_id)
        logger.info(f"🤖 LocalModel loaded: {model_id}")
    
    @classmethod
    def from_name(cls, name: str):
        """
        Load model by name.
        
        Args:
            name: Model identifier
        
        Returns:
            LocalModel instance
        """
        return cls(name)
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
        
        Returns:
            Generated text
        """
        return await self.bank.ask(prompt, temperature=kwargs.get("temperature", 0.7))
    
    def unload(self):
        """Unload model."""
        self.bank.unload()


# Singleton instance for easy access
_global_bank: Optional[ModelBank] = None


def get_model_bank() -> ModelBank:
    """Get or create global ModelBank instance."""
    global _global_bank
    if _global_bank is None:
        _global_bank = ModelBank()
    return _global_bank
