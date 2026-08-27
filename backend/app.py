from contextlib import asynccontextmanager
from typing import List

from dotenv import load_dotenv

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import models, schemas
from db.database import get_db
from agents.orient_agent import OrientIAAgent


load_dotenv()


# ============================================================
# AGENT
# ============================================================

agent_service: OrientIAAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent_service

    print("Initialisation de l'agent ORIENT'IA...")

    agent_service = OrientIAAgent()

    print("Agent ORIENT'IA prêt.")

    yield

    agent_service = None

    print("Agent ORIENT'IA arrêté.")


# ============================================================
# APPLICATION FASTAPI
# ============================================================

app = FastAPI(
    title="Orient'AI API",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SCHEMA CHAT
# ============================================================

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        description="Message ou question du candidat",
        example="J'ai eu 16 en maths et 14 en physique, quelle filière me correspond ?",
    )

    chat_history: list = Field(
        default_factory=list,
        description="Historique optionnel des échanges",
    )


# ============================================================
# UTILISATEURS
# ============================================================

@app.get(
    "/users/",
    response_model=List[schemas.User],
)
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return (
        db.query(models.User)
        .offset(skip)
        .limit(limit)
        .all()
    )


@app.get(
    "/users/{user_id}",
    response_model=schemas.User,
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@app.put(
    "/users/{user_id}",
    response_model=schemas.User,
)
def update_user(
    user_id: int,
    user: schemas.UserBase,
    db: Session = Depends(get_db),
):
    db_user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    for key, value in user.dict().items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)

    return db_user


@app.delete(
    "/users/{user_id}",
    response_model=schemas.User,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    db.delete(user)
    db.commit()

    return user


# ============================================================
# CHAT ORIENT'IA
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest) -> dict:

    if agent_service is None:
        raise HTTPException(
            status_code=503,
            detail="L'agent ORIENT'IA n'est pas encore initialisé.",
        )

    try:

        result = agent_service.run(
            user_message=request.message,
            chat_history=request.chat_history,
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne du serveur : {str(e)}",
        )