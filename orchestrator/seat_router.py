"""
Seat Router - Vector-Driven Role Assignment
Vertex Genesis v1.2.0

Zero-code, zero-names, pure field math.
Uses vector embeddings to match tasks to optimal models.
"""

import logging
import sqlite3
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import torch
import numpy as np
from sentence_transformers import SentenceTransformer

# Local imports
from model import LocalModel
from lifecycle import LifecycleMonitor
from hf_indexer import get_indexer

logger = logging.getLogger(__name__)

# Embedder – tiny, 384D
EMBED = SentenceTransformer('all-MiniLM-L6-v2')
INDEX_DB = Path('./agents/index.db')

# Seat vector store – seats[0] to seats[4]
SEATS: List[Optional[LocalModel]] = [None] * 5
SEAT_NAMES = ['Scribe', 'Gatekeeper', 'Balancer', 'Keeper', 'Echo']

# Lifecycle integration
lifecycle: Optional[LifecycleMonitor] = None


def init_seat_router(lifecycle_monitor: LifecycleMonitor):
    """
    Initialize seat router.
    
    Args:
        lifecycle_monitor: Lifecycle monitor instance
    """
    global lifecycle
    lifecycle = lifecycle_monitor
    
    # Ensure database directory exists
    INDEX_DB.parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    if not INDEX_DB.exists():
        db = sqlite3.connect(INDEX_DB)
        db.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                description TEXT,
                score REAL DEFAULT 1.0
            )
        ''')
        db.commit()
        db.close()
        logger.info("✅ Seat router database initialized")
    
    logger.info("🪑 Seat router initialized")


class Router:
    """
    Vector-driven seat assignment router.
    Matches tasks to optimal models using embeddings.
    """
    
    def __init__(self):
        self.db = sqlite3.connect(INDEX_DB, check_same_thread=False)
        self.cur = self.db.cursor()
        self.lock = threading.Lock()
        
        # Start periodic delta pull thread
        self.delta_thread = threading.Thread(target=self._delta_pull, daemon=True)
        self.delta_thread.start()
        
        logger.info("🪑 Router instance created")
    
    def _delta_pull(self):
        """Periodic model discovery and indexing using HuggingFace."""
        while True:
            try:
                # Use HuggingFace indexer for real-time discovery
                indexer = get_indexer()
                
                # Bulk index popular models (once per cycle)
                indexer.bulk_index_popular_models(limit=50)
                
                # Touch lifecycle
                if lifecycle:
                    lifecycle.touch()
                
                logger.info(f"🔄 Delta pull complete: HuggingFace index updated")
            except Exception as e:
                logger.error(f"❌ Delta pull error: {e}")
            
            # Sleep for 4 hours
            time.sleep(14400)
    
    def _reindex(self, models: List[Dict[str, Any]]):
        """
        Reindex models with embeddings.
        
        Args:
            models: List of model dictionaries with 'id' and 'desc' keys
        """
        with self.lock:
            for m in models:
                try:
                    # Generate embedding
                    vec = self._embed(m.get('desc', m.get('id', '')))
                    
                    # Store in database
                    self.cur.execute(
                        "INSERT OR REPLACE INTO models VALUES (?, ?, ?, ?)",
                        (m['id'], vec, m.get('desc', ''), m.get('score', 1.0))
                    )
                except Exception as e:
                    logger.error(f"❌ Reindex error for {m.get('id')}: {e}")
            
            self.db.commit()
    
    def _embed(self, text: str) -> bytes:
        """
        Generate embedding for text.
        
        Args:
            text: Input text
        
        Returns:
            Embedding as bytes
        """
        vec = EMBED.encode([text])[0]
        return torch.tensor(vec).cpu().numpy().tobytes()
    
    def _cosine_similarity(self, vec1: bytes, vec2: bytes) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            vec1: First embedding (bytes)
            vec2: Second embedding (bytes)
        
        Returns:
            Cosine similarity score
        """
        try:
            a = np.frombuffer(vec1, dtype=np.float32)
            b = np.frombuffer(vec2, dtype=np.float32)
            
            # Cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
        except Exception as e:
            logger.error(f"❌ Cosine similarity error: {e}")
            return 0.0
    
    def assign(self, seat_id: int, input_text: str) -> Dict[str, Any]:
        """
        Assign optimal model to seat based on input text.
        Uses HuggingFace indexer with real-time model addition.
        
        Args:
            seat_id: Seat index (0-4)
            input_text: Task description
        
        Returns:
            Assignment result dictionary
        """
        if not 0 <= seat_id < 5:
            raise ValueError(f"Invalid seat_id: {seat_id}. Must be 0-4.")
        
        try:
            # Use HuggingFace indexer for optimal model selection
            indexer = get_indexer()
            
            # Get optimal model with $0-cost priority
            optimal = indexer.get_optimal_model(
                task_description=input_text,
                prefer_local=True,
                max_cost=0.0,  # $0-cost priority
                max_params=7000  # Max 7B params for efficiency
            )
            
            if not optimal:
                raise RuntimeError("No suitable model found. Try indexing more models.")
            
            best_id = optimal['model_id']
            best_desc = optimal['description']
            best_sim = optimal['similarity']
            
            # Get alternatives
            alternatives = indexer.search_models(
                query=input_text,
                max_cost=0.0,
                max_params=7000,
                limit=4
            )[1:4]  # Skip first (already selected)
            
            # Assign to seat (lazy load)
            if SEATS[seat_id] is None or SEATS[seat_id].id != best_id:
                logger.info(f"🔄 Loading model {best_id} into seat {seat_id}")
                SEATS[seat_id] = LocalModel.from_name(best_id)
            
            # Touch lifecycle
            if lifecycle:
                lifecycle.touch()
            
            # Return confirmation payload
            return {
                "seat": SEAT_NAMES[seat_id],
                "seat_id": seat_id,
                "model": best_id,
                "description": best_desc,
                "context_match": round(best_sim, 3),
                "cost_per_1k_tokens": optimal['cost_per_1k_tokens'],
                "params_millions": optimal['params_millions'],
                "is_local": optimal['is_local'],
                "alternatives": [
                    {
                        "model": m['model_id'],
                        "similarity": round(m['similarity'], 3),
                        "params_millions": m['params_millions']
                    }
                    for m in alternatives
                ]
            }
        except Exception as e:
            logger.error(f"❌ Assign error: {e}")
            raise
    
    def get_seat_status(self, seat_id: int) -> Dict[str, Any]:
        """
        Get status of a specific seat.
        
        Args:
            seat_id: Seat index (0-4)
        
        Returns:
            Seat status dictionary
        """
        if not 0 <= seat_id < 5:
            raise ValueError(f"Invalid seat_id: {seat_id}")
        
        seat = SEATS[seat_id]
        return {
            "seat": SEAT_NAMES[seat_id],
            "seat_id": seat_id,
            "loaded": seat is not None,
            "model": seat.id if seat else None
        }
    
    def get_all_seats_status(self) -> List[Dict[str, Any]]:
        """
        Get status of all seats.
        
        Returns:
            List of seat status dictionaries
        """
        return [self.get_seat_status(i) for i in range(5)]
    
    def unload_seat(self, seat_id: int):
        """
        Unload model from seat.
        
        Args:
            seat_id: Seat index (0-4)
        """
        if not 0 <= seat_id < 5:
            raise ValueError(f"Invalid seat_id: {seat_id}")
        
        if SEATS[seat_id]:
            SEATS[seat_id].unload()
            SEATS[seat_id] = None
            logger.info(f"🧹 Seat {seat_id} unloaded")
    
    def unload_all_seats(self):
        """Unload all seats."""
        for i in range(5):
            self.unload_seat(i)
        logger.info("🧹 All seats unloaded")
    
    def list_indexed_models(self) -> List[Dict[str, Any]]:
        """
        List all indexed models.
        
        Returns:
            List of model dictionaries
        """
        with self.lock:
            self.cur.execute("SELECT id, description, score FROM models")
            rows = self.cur.fetchall()
        
        return [
            {"id": row[0], "description": row[1], "score": row[2]}
            for row in rows
        ]
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'db'):
            self.db.close()


# Global router instance
_global_router: Optional[Router] = None


def get_router() -> Router:
    """Get or create global router instance."""
    global _global_router
    if _global_router is None:
        _global_router = Router()
    return _global_router


# Simple usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize
    from lifecycle import LifecycleMonitor
    test_lifecycle = LifecycleMonitor(enabled=False)
    init_seat_router(test_lifecycle)
    
    # Create router
    router = Router()
    
    # Test assignment
    result = router.assign(3, "build async parser in Rust")
    print(f"Assignment result: {result}")
    
    # Check status
    status = router.get_all_seats_status()
    print(f"Seats status: {status}")
