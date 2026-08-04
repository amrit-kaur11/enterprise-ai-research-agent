import os
import numpy as np
from app.core.config import settings

class VectorStoreManager:
    """
    High-performance, zero-crash Vector Knowledge Base.
    Uses pure Python dense vector memory index for instant zero-crash cosine similarity operations.
    """
    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.memory_store = [] # [{id, text, embedding, metadata}]
        print("[VectorStore] Memory vector index initialized.")

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            vec = np.zeros(384, dtype=np.float32)
            words = text.lower().split()
            if words:
                for w in words:
                    idx = abs(hash(w)) % 384
                    vec[idx] += 1.0
                norm = np.linalg.norm(vec)
                if norm > 0:
                    vec = vec / norm
            embeddings.append(vec.tolist())
        return embeddings

    def add_documents(self, documents: list[str], metadatas: list[dict], ids: list[str]):
        if not documents:
            return
        embeddings = self.generate_embeddings(documents)
        for idx in range(len(documents)):
            self.memory_store.append({
                "id": ids[idx],
                "text": documents[idx],
                "embedding": embeddings[idx],
                "metadata": metadatas[idx] if idx < len(metadatas) else {}
            })

    def query_similar(self, query: str, n_results: int = 5, where_filter: dict = None) -> dict:
        query_vec = np.array(self.generate_embeddings([query])[0], dtype=np.float32)

        filtered = self.memory_store
        if where_filter:
            filtered = [
                item for item in self.memory_store
                if all(item["metadata"].get(k) == v for k, v in where_filter.items())
            ]

        if not filtered:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        scored = []
        for item in filtered:
            doc_vec = np.array(item["embedding"], dtype=np.float32)
            dot = np.dot(query_vec, doc_vec)
            norm_q = np.linalg.norm(query_vec)
            norm_d = np.linalg.norm(doc_vec)
            sim = dot / (norm_q * norm_d) if norm_q > 0 and norm_d > 0 else 0.0
            dist = 1.0 - float(sim)
            scored.append((dist, item))

        scored.sort(key=lambda x: x[0])
        top_k = scored[:n_results]

        return {
            "documents": [[x[1]["text"] for x in top_k]],
            "metadatas": [[x[1]["metadata"] for x in top_k]],
            "distances": [[x[0] for x in top_k]]
        }

vector_store = VectorStoreManager()
