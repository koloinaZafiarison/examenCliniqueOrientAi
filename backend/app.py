from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.orient_agent import orienter
from backend.gemini import generate_text

app = FastAPI(title="Orient'AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OrientationRequest(BaseModel):
    responses: dict[str, str] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/orient")
def orientation(request: OrientationRequest) -> dict:
    return orienter(request.responses)


@app.post("/api/chat")
def chat(request: ChatRequest) -> dict[str, str]:
    try:
        reply = generate_text(request.message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"reply": reply}