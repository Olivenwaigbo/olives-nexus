# rag.py
# Simplified version for deployment (ChromaDB removed)



CHROMA_DB_DIR   = "chroma_db"
COLLECTION_NAME = "dashboard_kb"
EMBED_MODEL     = "all-MiniLM-L6-v2"
TOP_K           = 5

# Load model once
_model = None





def retrieve(user_prompt: str, top_k: int = TOP_K) -> str:
    """
    Temporary retrieval function (ChromaDB removed).
    Returns placeholder context so the app runs without error.
    """
    return "Knowledge base is not connected yet."


def retrieve_with_metadata(user_prompt: str, top_k: int = TOP_K):
    """
    Temporary metadata function.
    """
    return "Knowledge base is not connected yet.", [], []