import psycopg
import numpy as np
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

DSN = "postgresql://aipe:aipe123@localhost:5432/aipe"
MODEL = SentenceTransformer("intfloat/multilingual-e5-large")

def query(question, *, candidate, k):
    vec = MODEL.encode([question], normalize_embeddings=True)[0].tolist()

    sql = """
    SELECT id, text, start, end, url,
           (embedding <=> %(vec)s) AS score
    FROM   transcript_chunks
    WHERE  (%(cand)s IS NULL OR candidate = %(cand)s)
    ORDER  BY embedding <=> %(vec)s
    LIMIT  %(k)s;
    """

    with psycopg.connect(DSN) as con:
        register_vector(con)
        return con.execute(sql, {"vec": vec, "cand": candidate, "k": k}).fetchall()