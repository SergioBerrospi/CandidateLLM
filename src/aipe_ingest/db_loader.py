import pandas as pd
import psycopg
import psycopg2.extras
from pgvector.psycopg import register_vector
import numpy as np
import pathlib
import os

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PARQUET = pathlib.Path(os.getenv("AIPE_PARQUET", REPO_ROOT / "datasets/processed/embeddings.parquet"))
DSN = os.getenv("AIPE_PG_DSN", "postgresql://aipe:aipe123@localhost:5433/aipe") 


def main():

    if not PARQUET.exists():
        raise FileNotFoundError(f"Parquet not found: {PARQUET}")


    df = pd.read_parquet(PARQUET)

    embed_col = "embedding" if "embedding" in df.columns else "embeddings"
    required = ["id", "text", "n_tokens", embed_col, "candidate", "role", "start", "end", "video_id"]
    missing = [c for c in required if c not in  df.columns]
    
    if missing:
        raise KeyError(f"Missing required columns in parquet file: {missing}")
    
    #Copy of the df
    df = df[required].copy()
    
    # Types
    df["id"] = df["id"].astype(str)
    df["n_tokens"]=df["n_tokens"].astype("Int64")
    df["start"] = df["start"].astype(float)
    df["end"]= df["end"].astype(float)


    # Ensuring embeddings are python lists of float
    df[embed_col] = df[embed_col].map(lambda v: [float(x) for x in (v.tolist() if hasattr(v, "tolist") else v)])

    # integrity check
    dim = len(df[embed_col].iloc[0])
    if dim != 1024:
        print(f"[warn] embedding dim = {dim} (schema expects 1024)")

    # Row generator
    def row_iter():
        for r in df.itertuples(index=False, name=None):
            _id, text, n_tokens, emb, cand, role, start, end, vid = r
            yield (
                _id,text, 
                int(n_tokens) if pd.notna(n_tokens) else None,
                emb, cand, role,
                float(start) if pd.notna(start) else None,
                float(end) if pd.notna(end) else None,
                vid,
            )

    sql = """
        INSERT INTO transcript_chunks
            (id, text, n_tokens, embedding, candidate, role, start, "end", video_id)
        VALUES
            (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING
    """

    with psycopg.connect(DSN, autocommit=True) as con:
        register_vector(con) # enable pgvector
        with con.cursor() as cur:
            
            cur.executemany(sql,row_iter())

    print(f"Inserted {len(df):,} rows")

if __name__ == '__main__':
    main()