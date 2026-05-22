from pathlib import Path
import json
import faiss
from sentence_transformers import SentenceTransformer

from app.core.config import INDEX_PATHS
import re

def clean_text(t: str) -> str:
    t = t.replace("\u00a0", " ")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)
    t = re.sub(r"(\w)\n(\w)", r"\1 \2", t)
    t = re.sub(r"\s+\n", "\n", t)
    t = re.sub(r"\n\s+", "\n", t)
    return t.strip()



_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def load_agent_index(agent: str):
    out_dir: Path = INDEX_PATHS[agent]
    index = faiss.read_index(str(out_dir / "index.faiss"))
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    chunks = meta["chunks"]
    pdf_file = meta.get("pdf_file", "")
    return index, chunks, pdf_file


def retrieve(agent: str, question: str, k: int = 4):
    index, chunks, pdf_file = load_agent_index(agent)

    model = get_model()
    q_emb = model.encode([question], normalize_embeddings=True)

    scores, ids = index.search(q_emb, k)
    ids = ids[0].tolist()
    scores = scores[0].tolist()

    results = []
    for i, s in zip(ids, scores):
        if i == -1:
            continue
        results.append({
            "text": clean_text(chunks[i]),
            "score": float(s),
            "source": pdf_file
        })

    return results
