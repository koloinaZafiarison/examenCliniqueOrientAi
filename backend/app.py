from fastapi import FastAPI
from pydantic import BaseModel, Field

from agents.orient_agent import orienter

app = FastAPI(title="Orient'AI API", version="0.1.0")


class OrientationRequest(BaseModel):
    responses: dict[str, str] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/orient")
def orientation(request: OrientationRequest) -> dict:
    return orienter(request.responses)