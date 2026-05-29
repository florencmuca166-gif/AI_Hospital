from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import json

from app.core.config import PDF_PATHS, INDEX_PATHS


def read_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        text = page.extract_text() or ""
        parts.append(text)
    return "\n".join(parts)


def build_and_save_index(agent: str, chunk_size: int = 900, chunk_overlap: int = 150):
    pdf_path = PDF_PATHS[agent]
    out_dir = INDEX_PATHS[agent]
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_text = read_pdf_text(pdf_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(raw_text)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, normalize_embeddings=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(out_dir / "index.faiss"))

    meta = {
        "agent": agent,
        "pdf_file": pdf_path.name,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "chunks": chunks,
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    for agent in ["reception", "doctors", "departments", "billing"]:
        build_and_save_index(agent)


if __name__ == "__main__":
    main()
