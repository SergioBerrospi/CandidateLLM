import pandas as pd
import psycopg
import psycopg2.extras
from pgvector.psycopg import register_vector
import numpy as np
import pathlib

PARQUET = pathlib.Path("datsets/processed/embeddings.parquet")
DSN = "postgresql://aipe:aipe123@localhost:5432/aipe"


def main():
    df = pd.read_parquet(PARQUET)
    rows = [
        (   
            r.id, r.text, int(r.n_tokens),
            r.embeddings.tolist(),
            r.candidate, r.role, r.speaker,
            float(r.start), float(r.end),
            r.get("video_id"), r.get("url"),
        )
        for r in df.itertuples()
    ]

    with psycopg.connect(DSN, autocommit=True) as con:
        register_vector(con)
        with con.cursor() as cur:
            cur.execute("TRUNCATE transcript_chunks")
            psycopg2.extras.execute_batch(
                cur,
                """INSERT INTO transcript_chunks
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                rows,
                page_size=1000
            )

    print(f"Inserted {len(rows):,} rows")

if __name__ == '__main__':
    main()