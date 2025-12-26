"""
HuggingFace Model Indexer - Real-Time Model Discovery
Vertex Genesis v1.3.0

Connects to HuggingFace API for real-time model discovery.
Dynamically adds missing models to index when requested.
Optimizes for $0-cost by prioritizing free/local models.
"""

import logging
import time
import json
import sqlite3
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
import httpx
from sentence_transformers import SentenceTransformer
from cost_optimizer import get_optimizer

logger = logging.getLogger(__name__)

# HuggingFace API
HF_API_BASE = "https://huggingface.co/api"
HF_MODELS_ENDPOINT = f"{HF_API_BASE}/models"

# Local cache
CACHE_DIR = Path('./agents')
CACHE_DIR.mkdir(exist_ok=True, parents=True)
INDEX_DB = CACHE_DIR / 'hf_index.db'

# Embedder for semantic search
EMBED = SentenceTransformer('all-MiniLM-L6-v2')


class HuggingFaceIndexer:
    """
    Real-time HuggingFace model indexer.
    Automatically adds missing models to index.
    Prioritizes free and local models for $0-cost optimization.
    """
    
    def __init__(self):
        self.db = sqlite3.connect(INDEX_DB, check_same_thread=False)
        self.cur = self.db.cursor()
        self.lock = threading.Lock()
        self.client = httpx.Client(timeout=30.0)
        
        # Initialize database
        self._init_db()
        
        logger.info("🤗 HuggingFace Indexer initialized")
    
    def _init_db(self):
        """Initialize database schema."""
        with self.lock:
            self.cur.execute('''
                CREATE TABLE IF NOT EXISTS hf_models (
                    model_id TEXT PRIMARY KEY,
                    model_name TEXT,
                    author TEXT,
                    description TEXT,
                    embedding BLOB,
                    downloads INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    tags TEXT,
                    pipeline_tag TEXT,
                    library_name TEXT,
                    is_local BOOLEAN DEFAULT 0,
                    is_free BOOLEAN DEFAULT 1,
                    cost_per_1k_tokens REAL DEFAULT 0.0,
                    params_millions INTEGER DEFAULT 0,
                    context_length INTEGER DEFAULT 0,
                    last_updated INTEGER,
                    added_timestamp INTEGER
                )
            ''')
            
            # Index for fast lookups
            self.cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_model_id ON hf_models(model_id)
            ''')
            self.cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_pipeline_tag ON hf_models(pipeline_tag)
            ''')
            self.cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_cost ON hf_models(cost_per_1k_tokens)
            ''')
            self.cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_params ON hf_models(params_millions)
            ''')
            
            self.db.commit()
            logger.info("✅ HuggingFace index database initialized")
    
    def _embed_text(self, text: str) -> bytes:
        """Generate embedding for text."""
        vec = EMBED.encode([text])[0]
        import torch
        return torch.tensor(vec).cpu().numpy().tobytes()
    
    def _fetch_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch model information from HuggingFace API.
        
        Args:
            model_id: HuggingFace model ID (e.g., "mistralai/Mistral-7B-Instruct-v0.2")
        
        Returns:
            Model information dictionary or None if not found
        """
        try:
            url = f"{HF_API_BASE}/models/{model_id}"
            response = self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Fetched model info: {model_id}")
                return data
            else:
                logger.warning(f"⚠️ Model not found on HuggingFace: {model_id}")
                return None
        except Exception as e:
            logger.error(f"❌ Error fetching model {model_id}: {e}")
            return None
    
    def _parse_model_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse HuggingFace API response into indexed format.
        
        Args:
            data: Raw API response
        
        Returns:
            Parsed model information
        """
        model_id = data.get('modelId', data.get('id', ''))
        author = data.get('author', model_id.split('/')[0] if '/' in model_id else '')
        model_name = model_id.split('/')[-1] if '/' in model_id else model_id
        
        # Extract metadata
        tags = data.get('tags', [])
        pipeline_tag = data.get('pipeline_tag', 'text-generation')
        library_name = data.get('library_name', 'transformers')
        downloads = data.get('downloads', 0)
        likes = data.get('likes', 0)
        
        # Description from card data or tags
        description = data.get('cardData', {}).get('description', '')
        if not description:
            description = f"{pipeline_tag} model by {author}"
        
        # Estimate parameters from model card or tags
        params_millions = 0
        for tag in tags:
            if 'b' in tag.lower() or 'billion' in tag.lower():
                try:
                    # Extract number (e.g., "7b" -> 7000)
                    num = ''.join(filter(str.isdigit, tag))
                    if num:
                        params_millions = int(num) * 1000
                except:
                    pass
            elif 'm' in tag.lower() or 'million' in tag.lower():
                try:
                    num = ''.join(filter(str.isdigit, tag))
                    if num:
                        params_millions = int(num)
                except:
                    pass
        
        # Context length estimation
        context_length = 0
        for tag in tags:
            if 'context' in tag.lower() or 'ctx' in tag.lower():
                try:
                    num = ''.join(filter(str.isdigit, tag))
                    if num:
                        context_length = int(num)
                except:
                    pass
        
        # Default context lengths by model type
        if context_length == 0:
            if 'mistral' in model_id.lower():
                context_length = 8192
            elif 'llama' in model_id.lower():
                context_length = 4096
            elif 'gpt' in model_id.lower():
                context_length = 4096
            else:
                context_length = 2048
        
        # Cost estimation ($0 for local/open-source)
        is_local = library_name in ['transformers', 'sentence-transformers', 'diffusers']
        is_free = True
        cost_per_1k_tokens = 0.0
        
        # Generate embedding
        embedding_text = f"{model_name} {description} {' '.join(tags[:5])}"
        embedding = self._embed_text(embedding_text)
        
        return {
            'model_id': model_id,
            'model_name': model_name,
            'author': author,
            'description': description,
            'embedding': embedding,
            'downloads': downloads,
            'likes': likes,
            'tags': json.dumps(tags),
            'pipeline_tag': pipeline_tag,
            'library_name': library_name,
            'is_local': is_local,
            'is_free': is_free,
            'cost_per_1k_tokens': cost_per_1k_tokens,
            'params_millions': params_millions,
            'context_length': context_length,
            'last_updated': int(time.time()),
            'added_timestamp': int(time.time())
        }
    
    def add_model_to_index(self, model_id: str) -> bool:
        """
        Add model to index by fetching from HuggingFace API.
        
        Args:
            model_id: HuggingFace model ID
        
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Check if already in index
            if self.is_model_indexed(model_id):
                logger.info(f"ℹ️ Model already indexed: {model_id}")
                return True
            
            # Fetch from HuggingFace
            data = self._fetch_model_info(model_id)
            if not data:
                logger.warning(f"⚠️ Could not fetch model: {model_id}")
                return False
            
            # Parse and insert
            parsed = self._parse_model_info(data)
            
            with self.lock:
                self.cur.execute('''
                    INSERT OR REPLACE INTO hf_models VALUES (
                        :model_id, :model_name, :author, :description, :embedding,
                        :downloads, :likes, :tags, :pipeline_tag, :library_name,
                        :is_local, :is_free, :cost_per_1k_tokens, :params_millions,
                        :context_length, :last_updated, :added_timestamp
                    )
                ''', parsed)
                self.db.commit()
            
            logger.info(f"✅ Added model to index: {model_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error adding model to index: {e}")
            return False
    
    def is_model_indexed(self, model_id: str) -> bool:
        """Check if model is already in index."""
        with self.lock:
            self.cur.execute("SELECT 1 FROM hf_models WHERE model_id = ?", (model_id,))
            return self.cur.fetchone() is not None
    
    def get_model_from_index(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get model from index, fetching from HuggingFace if missing.
        
        Args:
            model_id: HuggingFace model ID
        
        Returns:
            Model information dictionary or None
        """
        # Check index first
        with self.lock:
            self.cur.execute('''
                SELECT model_id, model_name, author, description, downloads, likes,
                       tags, pipeline_tag, library_name, is_local, is_free,
                       cost_per_1k_tokens, params_millions, context_length
                FROM hf_models WHERE model_id = ?
            ''', (model_id,))
            row = self.cur.fetchone()
        
        if row:
            logger.info(f"✅ Model found in index: {model_id}")
            return {
                'model_id': row[0],
                'model_name': row[1],
                'author': row[2],
                'description': row[3],
                'downloads': row[4],
                'likes': row[5],
                'tags': json.loads(row[6]),
                'pipeline_tag': row[7],
                'library_name': row[8],
                'is_local': bool(row[9]),
                'is_free': bool(row[10]),
                'cost_per_1k_tokens': row[11],
                'params_millions': row[12],
                'context_length': row[13]
            }
        
        # Not in index, fetch and add
        logger.info(f"🔍 Model not in index, fetching: {model_id}")
        if self.add_model_to_index(model_id):
            return self.get_model_from_index(model_id)
        
        return None
    
    def search_models(
        self,
        query: str,
        pipeline_tag: Optional[str] = None,
        max_cost: float = 0.0,
        max_params: Optional[int] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search models by semantic similarity with filters.
        
        Args:
            query: Search query
            pipeline_tag: Filter by pipeline tag (e.g., "text-generation")
            max_cost: Maximum cost per 1k tokens (default 0.0 for free only)
            max_params: Maximum parameters in millions
            limit: Maximum results to return
        
        Returns:
            List of matching models sorted by relevance
        """
        # Generate query embedding
        query_embedding = self._embed_text(query)
        
        # Build SQL query
        sql = '''
            SELECT model_id, model_name, author, description, downloads, likes,
                   tags, pipeline_tag, library_name, is_local, is_free,
                   cost_per_1k_tokens, params_millions, context_length, embedding
            FROM hf_models
            WHERE cost_per_1k_tokens <= ?
        '''
        params = [max_cost]
        
        if pipeline_tag:
            sql += " AND pipeline_tag = ?"
            params.append(pipeline_tag)
        
        if max_params:
            sql += " AND params_millions <= ?"
            params.append(max_params)
        
        with self.lock:
            self.cur.execute(sql, params)
            rows = self.cur.fetchall()
        
        # Calculate cosine similarities
        import numpy as np
        query_vec = np.frombuffer(query_embedding, dtype=np.float32)
        
        results = []
        for row in rows:
            model_vec = np.frombuffer(row[14], dtype=np.float32)
            
            # Cosine similarity
            dot_product = np.dot(query_vec, model_vec)
            norm_q = np.linalg.norm(query_vec)
            norm_m = np.linalg.norm(model_vec)
            
            if norm_q == 0 or norm_m == 0:
                similarity = 0.0
            else:
                similarity = float(dot_product / (norm_q * norm_m))
            
            results.append({
                'model_id': row[0],
                'model_name': row[1],
                'author': row[2],
                'description': row[3],
                'downloads': row[4],
                'likes': row[5],
                'tags': json.loads(row[6]),
                'pipeline_tag': row[7],
                'library_name': row[8],
                'is_local': bool(row[9]),
                'is_free': bool(row[10]),
                'cost_per_1k_tokens': row[11],
                'params_millions': row[12],
                'context_length': row[13],
                'similarity': similarity
            })
        
        # Sort by similarity (descending) then by downloads
        results.sort(key=lambda x: (x['similarity'], x['downloads']), reverse=True)
        
        return results[:limit]
    
    def get_optimal_model(
        self,
        task_description: str,
        pipeline_tag: Optional[str] = None,
        prefer_local: bool = True,
        max_cost: float = 0.0,
        max_params: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get optimal model for task with $0-cost priority.
        Uses cost optimizer to ensure best free option is chosen.
        
        Args:
            task_description: Description of the task
            pipeline_tag: Required pipeline tag
            prefer_local: Prefer local/downloadable models
            max_cost: Maximum acceptable cost (default 0.0)
            max_params: Maximum parameters in millions
        
        Returns:
            Optimal model or None
        """
        results = self.search_models(
            query=task_description,
            pipeline_tag=pipeline_tag,
            max_cost=max_cost,
            max_params=max_params,
            limit=20
        )
        
        if not results:
            return None
        
        # Add quality scores based on similarity and popularity
        for r in results:
            # Quality score: weighted combination of similarity, downloads, and params
            similarity_score = r['similarity']
            download_score = min(r['downloads'] / 100000, 1.0)  # Normalize to 0-1
            param_score = 1.0 - (r['params_millions'] / 10000)  # Prefer smaller models
            
            r['quality_score'] = (
                similarity_score * 0.6 +  # 60% weight on relevance
                download_score * 0.2 +    # 20% weight on popularity
                param_score * 0.2         # 20% weight on efficiency
            )
        
        # Use cost optimizer to choose best option
        optimizer = get_optimizer()
        decision = optimizer.evaluate_options(
            results,
            context=task_description,
            quality_threshold=0.5
        )
        
        # Find chosen model in results
        chosen = next(
            (m for m in results if m['model_id'] == decision.chosen_option),
            results[0]
        )
        
        logger.info(f"🎯 Optimal model selected: {chosen['model_id']} (cost: ${decision.cost_per_1k_tokens:.4f})")
        
        return chosen
    
    def bulk_index_popular_models(self, limit: int = 100):
        """
        Bulk index popular models from HuggingFace.
        
        Args:
            limit: Number of models to index
        """
        try:
            logger.info(f"🔍 Bulk indexing {limit} popular models...")
            
            # Fetch popular models
            response = self.client.get(
                HF_MODELS_ENDPOINT,
                params={
                    'sort': 'downloads',
                    'direction': -1,
                    'limit': limit,
                    'filter': 'text-generation'
                }
            )
            
            if response.status_code == 200:
                models = response.json()
                
                for model_data in models:
                    model_id = model_data.get('modelId', model_data.get('id'))
                    if model_id:
                        self.add_model_to_index(model_id)
                
                logger.info(f"✅ Bulk indexing complete: {len(models)} models")
            else:
                logger.error(f"❌ Bulk indexing failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ Bulk indexing error: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'db'):
            self.db.close()
        if hasattr(self, 'client'):
            self.client.close()


# Global indexer instance
_global_indexer: Optional[HuggingFaceIndexer] = None


def get_indexer() -> HuggingFaceIndexer:
    """Get or create global indexer instance."""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = HuggingFaceIndexer()
    return _global_indexer


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    indexer = HuggingFaceIndexer()
    
    # Test: Add specific model
    indexer.add_model_to_index("mistralai/Mistral-7B-Instruct-v0.2")
    
    # Test: Get model (will fetch if missing)
    model = indexer.get_model_from_index("microsoft/phi-3-mini-4k-instruct")
    print(f"Model: {model}")
    
    # Test: Search models
    results = indexer.search_models("fast code generation", max_cost=0.0, limit=5)
    print(f"Search results: {len(results)}")
    for r in results:
        print(f"  - {r['model_id']} (similarity: {r['similarity']:.3f})")
    
    # Test: Get optimal model
    optimal = indexer.get_optimal_model("translate text from image", pipeline_tag="text-generation")
    print(f"Optimal model: {optimal['model_id'] if optimal else None}")
