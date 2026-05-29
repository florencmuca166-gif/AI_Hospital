from app.rag.retriever import retrieve
from app.agents.common import llm_answer

SPECIALTY_TRIGGERS = [
    "cilët janë", "cilet jane",
    "kush janë", "kush jane",
    "a keni", "keni",
    "mjekët e", "mjeket e",
    "specialist", "specialistë",
    "doktor", "mjek"
]

def handle_doctors(question: str, history=None) -> dict:
    if history is None:
        history = []

    q = question.lower().strip()

    # Pyetje për specialitet (p.sh. pediatër, neurolog, dermatolog)
    if any(t in q for t in SPECIALTY_TRIGGERS):
        hits = retrieve("doctors", question, k=10)
    else:
        hits = retrieve("doctors", question, k=4)

    context = "\n\n".join([h["text"] for h in hits]) if hits else ""

    final_answer = llm_answer(
        question,
        context,
        history=history
    )

    return {
        "agent": "doctors",
        "answer": final_answer,
        "sources": [{"file": h["source"], "score": h["score"]} for h in hits]
    }
