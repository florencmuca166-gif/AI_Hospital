import sys
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv(".env", override=True)

print("Testing retrieval...")
from app.rag.retriever import retrieve
hits = retrieve("reception", "orari", k=3)
print(f"Retrieved {len(hits)} chunks")

print("Testing LLM...")
from app.rag.llm import generate_answer
answer = generate_answer("What are the visiting hours?", hits[0]["text"] if hits else "", history=[])
print("Answer:", answer)
