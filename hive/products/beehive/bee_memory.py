import json
import os

import requests

# THE BEEHIVE: Local Vector Memory System
# Ingests docs/ and knowledge/ into a local vector store using Ollama.

# Configuration
OLLAMA_API = "http://localhost:11434/api/embeddings"
MODEL = "nomic-embed-text" # Optimized for RAG
INDEX_FILE = "beehive_index.json"

ROOT_DIRS = [
    "../../../docs",
    "../../../knowledge"
]

def check_ollama():
    try:
        # Check tags to see if model exists
        r = requests.get("http://localhost:11434/api/tags")
        if r.status_code == 200:
            models = [m['name'] for m in r.json()['models']]
            print(f"✅ Ollama Online. Models detected: {len(models)}")
            if MODEL not in models and f"{MODEL}:latest" not in models:
                print(f"⚠️  WARNING: Requested model '{MODEL}' not found. Run 'ollama pull {MODEL}'")
                return False
            return True
        return False
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Failed to check Ollama status: {e}")
        return False

def get_embedding(text):
    if not text or len(text) < 10: return None
    try:
        response = requests.post(OLLAMA_API, json={
            "model": MODEL,
            "prompt": text
        })
        if response.status_code == 200:
            return response.json()["embedding"]
    except Exception as e:
        print(f"❌ Embedding Error: {e}")
    return None

def ingest():
    print("🐝 THE BEEHIVE: Starting Ingestion (Full Vectorization)...")

    if not check_ollama():
        print("❌ OLLAMA OFFLINE or UNREACHABLE.")
        print("   Please run 'ollama serve' in a separate terminal.")
        return

    vectors = []

    # Simple recursive walk
    count = 0
    for root_path in ROOT_DIRS:
        abs_root = os.path.abspath(os.path.join(os.path.dirname(__file__), root_path))
        print(f"   Scanning: {abs_root}")

        if not os.path.exists(abs_root):
            print(f"⚠️  PATH NOT FOUND: {abs_root}")
            continue

        for dirpath, _, filenames in os.walk(abs_root):
            for f in filenames:
                if f.endswith(".md") or f.endswith(".txt"):
                    fullpath = os.path.join(dirpath, f)
                    try:
                        with open(fullpath, encoding='utf-8') as file:
                            content = file.read()

                        # Naive chunking (paragraphs)
                        chunks = content.split("\n\n")
                        for i, chunk in enumerate(chunks):
                            if len(chunk) < 50: continue # Skip noise

                            # Indexing Logic:
                            # 1. First chunk is usually the summary/header -> High Priority
                            # 2. Limit to 3 chunks per file for MVP speed (unless critical)
                            if i > 5: break

                            print(f"      Embed: {f} [{i}]")
                            vec = get_embedding(chunk)

                            if vec:
                                vectors.append({
                                    "source": f,
                                    "path": fullpath,
                                    "preview": chunk[:100],
                                    "vector": vec
                                })
                                count += 1

                    except Exception as e:
                        print(f"   Skipped {f}: {e}")

    print(f"✅ Indexed {count} vector segments.")

    print("   To enable full vectorization, uncomment line 86.")

    with open(INDEX_FILE, 'w') as f:
        json.dump(vectors, f, indent=2)
    print(f"💾 Index saved to {INDEX_FILE}")

if __name__ == "__main__":
    ingest()
