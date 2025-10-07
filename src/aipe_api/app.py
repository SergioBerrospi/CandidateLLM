from typing import Optional, List
import os
import psycopg
from fastapi import FastAPI, Query, Body
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from pgvector.psycopg import register_vector, Vector
from sentence_transformers import SentenceTransformer
import pandas as pd
from uuid import UUID

class Settings(BaseSettings):
    pg_dsn: str = "postgresql://aipe:aipe123@localhost:5433/aipe"
    model_name: str = "intfloat/multilingual-e5-large"
    default_top_k: int = 5
    llm_model : str = "llama3.1:8b-instruct"


settings = Settings()

# app + Global Resources
app = FastAPI(title="AI Candidate Explorer API", version="0.1.0")
model =  SentenceTransformer(settings.model_name)

def embed_query(text:str) -> Vector:
    v = model.encode([f"query: {text}"], normalize_embeddings=True)[0].astype("float32").tolist()
    return Vector(v)

def fetch_df(sql: str, params=None):    
    with psycopg.connect(settings.pg_dsn) as con:
        register_vector(con)
        return pd.read_sql(sql, con, params=params)

# models

class Hit(BaseModel):
    id: UUID
    candidate: Optional[str] = None
    text: str
    start: float
    video_id: str
    score: float

class AnswerRequest(BaseModel):
    question: str
    candidate: Optional[str] = None
    k: int = settings.default_top_k

class AnswerResponse(BaseModel):
    answer: str
    sources: List[Hit]


# endpoints

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/candidates")
def candidates():
    df = fetch_df("""SELECT candidate, COUNT(*) AS n
                     FROM transcript_chunks
                     GROUP BY 1
                     ORDER BY 2 DESC""")
    return [{"candidate":r["candidate"], "n": int(r["n"])} for _, r in df.iterrows()]

@app.get("/search", response_model = List[Hit])
def search(question: str, candidate: Optional[str]=Query(None), k: int = Query(settings.default_top_k, ge=1, le=50),):
    qv = embed_query(question)
    where = "WHERE candidate = %s" if candidate else ""
    params = [qv] + ([candidate] if candidate else []) + [qv, k]
    sql = f"""
        SELECT id, candidate, text, start, "end", video_id,
               1 - (embedding <=> %s) AS score
        FROM transcript_chunks
        {where}
        ORDER BY embedding <=> %s
        LIMIT %s
    """
    df = fetch_df(sql, params=params)
    return [
        Hit(
            id=str(row["id"]),
            candidate=row.get("candidate"),
            text=row["text"],
            start=float(row["start"]),
            end=float(row["end"]),
            video_id=row["video_id"],
            score=float(row["score"]),
        )
        for _, row in df.iterrows()
    ]

@app.post("/answer", response_model = AnswerResponse)
def answer(req: AnswerRequest = Body(...)):
    hits= search(req.question, req.candidate, req.k)

    #MVP
    ctx = "\n".join(
        f"- ({h.video_id} [{h.start:.0f}-{h.end:.0f}]) {h.text}" for h in hits
    )
    reply = (
        f"Pregunta: {req.question}\n\n"
        f"Fuentes:\n{ctx}\n\n"
        f"Resumen (MVP): sintetiza con LLM aquí."
    )
    return AnswerResponse(answer=reply, sources=hits)