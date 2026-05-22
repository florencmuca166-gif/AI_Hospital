from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.agents.controller import route_question, route_question_stream
import json

router = APIRouter()

@router.post("/ask")
def ask(payload: dict):
    question = payload.get("question", "").strip()
    history = payload.get("history", [])

    if not question:
        return {"answer": "Ju lutem shkruani një pyetje.", "agent": None, "sources": []}

    return route_question(question, history=history)


@router.post("/ask/stream")
def ask_stream(payload: dict):
    question = payload.get("question", "").strip()
    history = payload.get("history", [])

    if not question:
        async def empty():
            yield f"data: {json.dumps({'done': True, 'answer': 'Ju lutem shkruani një pyetje.'})}\n\n"
        return StreamingResponse(empty(), media_type="text/event-stream")

    def event_stream():
        for chunk in route_question_stream(question, history=history):
            yield f"data: {json.dumps(chunk)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

