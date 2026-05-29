from app.rag.llm import generate_answer, generate_answer_stream

def llm_answer(question: str, context: str, history=None) -> str:
    if history is None:
        history = []
    context = context or ""
    return generate_answer(question, context, history=history)

def llm_answer_stream(question: str, context: str, history=None):
    if history is None:
        history = []
    context = context or ""
    yield from generate_answer_stream(question, context, history=history)
