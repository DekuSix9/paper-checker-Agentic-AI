import os
import math
from typing import List, Dict, Any, Optional

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")


class FastLocalEmbeddingFunction:
    """Fast local embedding function compatible with ChromaDB requiring 0 external downloads."""

    def _embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            vec = [0.0] * 384
            words = text.lower().split()
            for idx, word in enumerate(words):
                h = abs(hash(word)) % 384
                vec[h] += 1.0 / (idx + 1)
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            embeddings.append([v / norm for v in vec])
        return embeddings

    def __call__(self, input: Any = None, texts: Any = None) -> Any:
        inp = input if input is not None else texts
        if isinstance(inp, str):
            return self._embed([inp])
        return self._embed(list(inp or []))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, input: Any = None, query: Any = None) -> List[float]:
        target = input if input is not None else query
        q_str = target if isinstance(target, str) else str(target or "")
        return self._embed([q_str])[0]

    def name(self) -> str:
        return "FastLocalEmbeddingFunction"


class VectorStoreManager:
    """ChromaDB collection browser & vector store manager."""

    def __init__(self, db_path: str = CHROMA_PATH):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        self.client = None
        self.embedding_fn = FastLocalEmbeddingFunction()
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=self.db_path)
        except Exception as e:
            print(f"[VectorStoreManager Warning] ChromaDB initialization fallback: {e}")
            self.client = None

    def get_or_create_collection(self, collection_name: str):
        if self.client:
            try:
                return self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn
                )
            except Exception:
                try:
                    self.client.delete_collection(name=collection_name)
                except Exception:
                    pass
                return self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_fn
                )
        return None

    def add_documents(self, collection_name: str, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        if self.client:
            collection = self.get_or_create_collection(collection_name)
            collection.upsert(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, collection_name: str, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        if self.client:
            try:
                collection = self.get_or_create_collection(collection_name)
                results = collection.query(query_texts=[query_text], n_results=n_results)
                output = []
                docs = results.get("documents", [[]])[0]
                metas = results.get("metadatas", [[]])[0]
                distances = results.get("distances", [[]])[0] if results.get("distances") else [0.0]*len(docs)
                for doc, meta, dist in zip(docs, metas, distances):
                    output.append({"document": doc, "metadata": meta, "score": dist})
                return output
            except Exception as e:
                print(f"[VectorStoreManager query error] {e}")
        return []

    def list_collections(self) -> List[str]:
        if self.client:
            try:
                cols = self.client.list_collections()
                names = [c.name for c in cols]
                return names if names else ["paper_chunks", "related_work", "past_reviews"]
            except Exception:
                pass
        return ["paper_chunks", "related_work", "past_reviews"]


# Singleton instance
vector_store = VectorStoreManager()
