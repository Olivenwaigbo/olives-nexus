# rag.py
# RAG = Retrieval Augmented Generation
# This file searches ChromaDB for knowledge relevant to the user's prompt
# and returns it as context for the LLM

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DB_DIR   = "chroma_db"
COLLECTION_NAME = "dashboard_kb"
EMBED_MODEL     = "all-MiniLM-L6-v2"
TOP_K           = 5   # how many chunks to retrieve per query

# Load model once when this file is imported (not on every search)
_model      = None
_collection = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client      = chromadb.PersistentClient(path=CHROMA_DB_DIR)
        _collection = client.get_collection(COLLECTION_NAME)
    return _collection


def retrieve(user_prompt: str, top_k: int = TOP_K) -> str:
    """
    Search the knowledge base for chunks relevant to the user's prompt.
    Returns a single string of context ready to inject into the LLM prompt.
    """
    model      = _get_model()
    collection = _get_collection()

    # Embed the user's question
    query_embedding = model.encode([user_prompt]).tolist()

    # Search ChromaDB for the most similar chunks
    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = top_k,
    )

    # Pull out the text chunks from the results
    chunks = results["documents"][0]   # list of matching text chunks

    if not chunks:
        return "No relevant knowledge found."

    # Join them into one block of context
    context = "\n\n---\n\n".join(chunks)
    return context


def retrieve_with_metadata(user_prompt: str, top_k: int = TOP_K):
    """
    Same as retrieve() but also returns which domains were matched.
    Useful for debugging or showing the user where info came from.
    """
    model      = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([user_prompt]).tolist()

    results = collection.query(
        query_embeddings = query_embedding,
        n_results        = top_k,
        include          = ["documents", "metadatas", "distances"],
    )

    chunks    = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    items = []
    for chunk, meta, dist in zip(chunks, metadatas, distances):
        items.append({
            "text":     chunk,
            "domain":   meta.get("domain", "unknown"),
            "filename": meta.get("filename", "unknown"),
            "score":    round(1 - dist, 3),   # convert distance to similarity score
        })

    context = "\n\n---\n\n".join([item["text"] for item in items])
    domains  = list({item["domain"] for item in items})

    return context, domains, items
