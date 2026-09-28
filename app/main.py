import os
from fastapi import FastAPI
from pydantic import BaseModel, Field
from app.agent import build
from app.llm import get_llm
from app.memory import Memory

api = FastAPI(title="Planner-Executor Agent")
_llm, _sessions = get_llm(), {}

class Chat(BaseModel):
    session_id: str = Field(min_length=1, max_length=64)
    question: str = Field(min_length=1, max_length=500)

@api.get("/health")
def health():
    return {"status": "ok"}

@api.post("/chat")
def chat(c: Chat):
    mem = _sessions.setdefault(c.session_id, Memory())
    out = build(_llm, mem, os.getenv("PROMPT_VERSION", "v2")).invoke({"question": c.question})
    return {"answer": out["answer"], "plan": out["plan"], "results": out["results"]}
