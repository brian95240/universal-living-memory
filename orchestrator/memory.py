import os, time, gc, uuid, logging
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

logger = logging.getLogger("VertexMemory")

class VertexMemoryEngine:
    def __init__(self):
        self.client = QdrantClient(host="qdrant", port=6333)
        self._embed_model = None
        self._last_used = 0

    def _get_model(self):
        if not self._embed_model:
            logger.info("🧠 Hydrating Embedding Model")
            from fastembed import TextEmbedding
            self._embed_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self._last_used = time.time()
        return self._embed_model

    def _collapse_check(self):
        if self._embed_model and (time.time() - self._last_used > 600):
            logger.info("🧊 Collapsing Embedding Model")
            self._embed_model = None
            gc.collect()

    async def recall(self, query):
        try:
            self._collapse_check()
            model = self._get_model()
            vector = list(model.embed([query]))[0]
            hits = self.client.search(collection_name="memory", query_vector=vector, limit=5)
            return "\n".join([f"- {h.payload['text']}" for h in hits])
        except Exception:
            return ""

    async def memorize(self, user, ai):
        try:
            self._collapse_check()
            text = f"User: {user} | AI: {ai}"
            vector = list(self._get_model().embed([text]))[0]
            try:
                self.client.create_collection("memory", vectors_config=qmodels.VectorParams(size=384, distance=qmodels.Distance.COSINE))
            except: pass
            
            self.client.upsert(collection_name="memory", points=[
                qmodels.PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"text": text, "timestamp": time.time()})
            ])
        except Exception as e:
            logger.error(f"Memorize failed: {e}")
