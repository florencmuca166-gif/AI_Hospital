from fastapi import FastAPI
from app.api.routes import router
import os
import app.agents.reception as reception_mod
import app.agents.controller as controller_mod

app = FastAPI(title="Hygeia Hospital AI Backend")
app.include_router(router)

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/debug")
def debug():
    return {
        "cwd": os.getcwd(),
        "reception_file": reception_mod.__file__,
        "controller_file": controller_mod.__file__,
    }