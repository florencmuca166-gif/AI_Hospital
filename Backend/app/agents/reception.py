from app.rag.retriever import retrieve
from app.agents.common import llm_answer


def handle_reception(question: str, history=None) -> dict:
    if history is None:
        history = []

    # Marrim disa chunk-e nga reception.pdf
    # LLM do të vendosë çfarë të përdorë bazuar në rregullat e prompt-it
    hits = retrieve("reception", question, k=10)

    context = "\n\n".join([h["text"] for h in hits]) if hits else ""

    final_answer = llm_answer(
        question=question,
        context=context,
        history=history
    )

    return {
        "agent": "reception",
        "answer": final_answer,
        "sources": [
            {"file": h["source"], "score": h["score"]}
            for h in hits
        ]
    }
