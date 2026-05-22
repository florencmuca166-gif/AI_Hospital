from app.rag.retriever import retrieve
from app.agents.common import llm_answer

def is_package_question(question: str) -> bool:
    keywords = [
        "paket",
        "paketa",
        "lindje",
        "kushton",
        "çmim",
        "check",
        "check-up"
    ]
    q = question.lower()
    return any(k in q for k in keywords)


def handle_billing(question: str, history=None) -> dict:
    if history is None:
        history = []

    # 🔑 Nëse pyetja është për paketë → merr më shumë chunk-e
    if is_package_question(question):
        hits = retrieve("billing", question, k=6)
    else:
        hits = retrieve("billing", question, k=2)

    context = "\n\n".join([h["text"] for h in hits]) if hits else ""

    final_answer = llm_answer(
        question,
        context,
        history=history
    )

    return {
        "agent": "billing",
        "answer": final_answer,
        "sources": [{"file": h["source"], "score": h["score"]} for h in hits]
    }
