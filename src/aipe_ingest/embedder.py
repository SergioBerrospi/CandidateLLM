import argparse, math, pathlib
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

DEFAULT_MODEL = "intfloat/multilingual-e5-large"


def encode_chunks(in_path, out_path, model_name=DEFAULT_MODEL, batch_size=128):
    """Read chunk.parquet, write embeddings.parquet with a new column `embedding`"""
    df = pd.read_parquet(in_path)
    print(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name,
                                device="cuda" if model_name.endswith('8B') else "cpu")
    
    all_vecs = []
    n_batches = math.ceil(len(df)/batch_size)

    for i in tqdm(range(n_batches), desc="Embedding process"):
        batch = df["text"][i * batch_size : (i+1) * batch_size].tolist()
        vecs = model.encode(
            batch,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        all_vecs.extend(vecs)

    df["embeddings"] = [np.asarray(v, dtype=np.float32) for v in all_vecs]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out_path, index=False)
    print(f"Saved {len(df):,} rows --> {out_path}")

if __name__ == '__main__':
    
    p = argparse.ArgumentParser(description="Encode transcript chunks into vectors")
    p.add_argument("--input", "-i", dest="parquet_in", default="datasets/processed/chunks.parquet",
                   help="Input chunks Parquet")
    p.add_argument("--output", "-o", dest="parquet_out", default="datasets/processed/embeddings.parquet",
                   help="Output Parquet with `embedding` column")
    p.add_argument("--model","-m", default=DEFAULT_MODEL,
                   help="Any SentenceTransformer or HuggingFace embedding model")
    p.add_argument("--batch","-b", type=int, default=128,help="Batch size for model.encode()")
    args = p.parse_args()

    encode_chunks(
        pathlib.Path(args.parquet_in),
        pathlib.Path(args.parquet_out),
        args.model,
        args.batch
    )