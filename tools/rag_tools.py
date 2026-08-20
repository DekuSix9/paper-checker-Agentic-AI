import re
from typing import List, Dict, Any
from memory.vector_store import vector_store


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split paper text into overlapping chunks."""
    words = text.split()
    if not words:
        return []
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks


def index_paper_chunks(paper_raw_text: str, paper_id: str = "doc_1") -> int:
    """Chunk and index paper raw text into ChromaDB vector store."""
    chunks = chunk_text(paper_raw_text)
    documents = []
    metadatas = []
    ids = []
    
    for idx, chunk in enumerate(chunks):
        documents.append(chunk)
        metadatas.append({"paper_id": paper_id, "chunk_index": idx})
        ids.append(f"{paper_id}_chunk_{idx}")

    vector_store.add_documents(
        collection_name="paper_chunks",
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    return len(chunks)


def query_paper_chunks(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """Query paper chunks from ChromaDB vector store."""
    return vector_store.query(
        collection_name="paper_chunks",
        query_text=query,
        n_results=n_results
    )
