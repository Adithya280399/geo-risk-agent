import os, json, faiss, numpy as np, logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")
log = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

FAISS_INDEX_PATH    = "faiss_index/articles.index"
FAISS_METADATA_PATH = "faiss_index/articles_metadata.json"
EMBED_MODEL         = "text-embedding-3-small"

_index    = None
_metadata = None

def load_index():
    global _index, _metadata
    if _index is None:
        _index = faiss.read_index(FAISS_INDEX_PATH)
        with open(FAISS_METADATA_PATH) as f:
            _metadata = json.load(f)
        log.info(f"FAISS index loaded — {_index.ntotal} vectors")

def retrieve(query: str, top_k: int = 8) -> list[dict]:
    load_index()
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=[query]
    )
    query_vec = np.array([response.data[0].embedding], dtype="float32")
    distances, indices = _index.search(query_vec, top_k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        article = _metadata[idx].copy()
        article["distance"] = float(dist)
        results.append(article)
    return results