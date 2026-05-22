from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import os
import app.agents.reception as reception_mod
import app.agents.controller as controller_mod

app = FastAPI(title="Hygeia Hospital AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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