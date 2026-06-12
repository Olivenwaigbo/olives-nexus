# ingest.py
# Run this ONCE to load your knowledge base into ChromaDB
# After running, a folder called "chroma_db" will appear in your project

import os
import chromadb
from sentence_transformers import SentenceTransformer

# ── Settings ──────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE_DIR = "knowledge_base"   # folder with your .md files
CHROMA_DB_DIR      = "chroma_db"        # where ChromaDB saves its data
COLLECTION_NAME    = "dashboard_kb"     # name of the collection inside ChromaDB
CHUNK_SIZE         = 30                 # lines per chunk (smaller = more precise search)
EMBED_MODEL        = "all-MiniLM-L6-v2" # free, fast, runs locally
# ──────────────────────────────────────────────────────────────────────────────


def load_markdown_files(base_dir):
    """Walk the knowledge_base folder and return all .md file contents."""
    docs = []
    for domain in os.listdir(base_dir):
        domain_path = os.path.join(base_dir, domain)
        if not os.path.isdir(domain_path):
            continue
        for filename in os.listdir(domain_path):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(domain_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            docs.append({
                "domain":   domain,
                "filename": filename,
                "content":  content,
            })
            print(f"  Loaded: {domain}/{filename} ({len(content)} chars)")
    return docs


def chunk_text(text, chunk_size=CHUNK_SIZE):
    """Split text into chunks of ~chunk_size lines so each chunk fits in an embedding."""
    lines  = text.split("\n")
    chunks = []
    for i in range(0, len(lines), chunk_size):
        chunk = "\n".join(lines[i : i + chunk_size]).strip()
        if chunk:                          # skip empty chunks
            chunks.append(chunk)
    return chunks


def main():
    print("\n=== Dashboard LLM — Knowledge Base Ingestion ===\n")

    # 1. Load all markdown files
    print("Step 1: Loading markdown files...")
    docs = load_markdown_files(KNOWLEDGE_BASE_DIR)
    if not docs:
        print("ERROR: No .md files found in knowledge_base/")
        print("Make sure you have: knowledge_base/business_finance/knowledge.md etc.")
        return
    print(f"  Found {len(docs)} file(s)\n")

    # 2. Load the embedding model (downloads ~80MB first time, cached after)
    print("Step 2: Loading embedding model (may take a minute first time)...")
    model = SentenceTransformer(EMBED_MODEL)
    print("  Model ready\n")

    # 3. Set up ChromaDB
    print("Step 3: Setting up ChromaDB...")
    client     = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    # Delete old collection if it exists (so re-running stays clean)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("  Cleared old collection")
    except Exception:
        pass
    collection = client.create_collection(COLLECTION_NAME)
    print("  Collection created\n")

    # 4. Chunk, embed, and store everything
    print("Step 4: Embedding and storing chunks...")
    total_chunks = 0
    for doc in docs:
        chunks = chunk_text(doc["content"])
        if not chunks:
            continue

        embeddings = model.encode(chunks).tolist()

        ids       = [f"{doc['domain']}_{total_chunks + i}" for i in range(len(chunks))]
        metadatas = [{"domain": doc["domain"], "filename": doc["filename"]} for _ in chunks]

        collection.add(
            ids        = ids,
            documents  = chunks,
            embeddings = embeddings,
            metadatas  = metadatas,
        )
        print(f"  {doc['domain']}: {len(chunks)} chunks stored")
        total_chunks += len(chunks)

    print(f"\n✓ Done! {total_chunks} total chunks stored in ChromaDB")
    print(f"✓ Database saved to: ./{CHROMA_DB_DIR}/")
    print("\nYou can now run:  streamlit run app.py\n")


if __name__ == "__main__":
    main()
