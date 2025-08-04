CREATE EXTENSION IF NO EXISTS vector;

DROP TABLE IF EXISTS transcript_chunks;

CREATE TABLE transcript_chunks (
    id        UUID PRIMARY KEY,
    text      TEXT,
    n_tokens  INT,
    embedding VECTOR(384),
    candidate TEXT,
    role      TEXT,
    speaker   TEXT,
    start     REAL,
    end       REAL,
    video_id  TEXT,
    url       TEXT
);

-- Cosine-distance using HNSW index
CREATE INDEX ON transcript_chunks
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 128);