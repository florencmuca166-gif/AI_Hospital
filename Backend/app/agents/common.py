from app.rag.llm import generate_answer

def llm_answer(question: str, context: str, history=None) -> str:
    if history is None:
        history = []
    context = context or ""
    return generate_answer(question, context, history=history)
