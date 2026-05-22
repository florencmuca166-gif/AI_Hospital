from fastapi import APIRouter
from app.agents.controller import route_question

router = APIRouter()

@router.post("/ask")
def ask(payload: dict):
    question = payload.get("question", "").strip()
    history = payload.get("history", [])

    if not question:
        return {"answer": "Ju lutem shkruani një pyetje.", "agent": None, "sources": []}

    return route_question(question, history=history)

