from app.rag.retriever import retrieve
from app.agents.common import llm_answer

GENERAL_DEPTS_TRIGGERS = [
    "cilat departamente", "cilet departamente", "departamente ofron",
    "lista e departamenteve", "te gjitha departamentet", "departamentet"
]

def handle_departments(question: str, history=None) -> dict:
    if history is None:
        history = []

    q = question.lower().strip()

    if any(t in q for t in GENERAL_DEPTS_TRIGGERS):
        hits = retrieve("departments", "Departamentet sipas Grupeve Funksionale", k=18)
    else:
        hits = retrieve("departments", question, k=6)

    context = "\n\n".join([h["text"] for h in hits]) if hits else ""

    final_answer = llm_answer(
        question,
        context,
        history=history
    )

    return {
        "agent": "departments",
        "answer": final_answer,
        "sources": [{"file": h["source"], "score": h["score"]} for h in hits]
    }
