import json
import uuid
import pathlib

from typing import Any, Dict, Iterator, List

import pandas as pd
import nltk
import sys

def get_tokenizer(model_name: str | None = None):
    if model_name is None:
        import tiktoken
        enc =  tiktoken.get_encoding("cl100k_base")
        return lambda txt: enc.encode(txt, disallowed_special=[])
    
    # HuggingFace path
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    return lambda txt: tok(txt, add_special_tokens=False)["input_ids"]

# Default Tokenizer
TOKENIZER = get_tokenizer()

# Chunk-size hyper-parameters
CHUNK_SIZE = 384
CHUNK_OVERLAP = 64



## Helper Functions
def _token_len(text) -> int:
    """Count the number of tokens used"""

    return len(TOKENIZER(text))

def _sentences(text) -> List[str]:
    """Spanish sentences splitter using NLTK"""

    return nltk.sent_tokenize(text, language="spanish")

def _flush(buf: List[str], seg: Dict[str, Any], meta: Dict[str,Any]) -> Dict[str,Any]:
    chunk_text = " ".join(buf)
    return {
        "id": str(uuid.uuid4()),
        "text": chunk_text,
        "n_tokens": _token_len(chunk_text),
        "speaker": seg["speaker"],
        "start": seg["start"],
        "end": seg["end"],
        **meta,

    }

def chunk_segment(seg: Dict[str, Any], meta: Dict[str,Any], chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterator[Dict[str, Any]]:
    """ Yield overlapping chunks from one transcript segment"""
    
    buf = []
    token_count = 0

    for sent in _sentences(seg["text"]):
        sent_tokens = _token_len(sent)

        if token_count + sent_tokens > chunk_size and buf:
            yield _flush(buf, seg, meta)
            while buf and token_count> overlap:
                token_count -= _token_len(buf.pop(0))

        
        buf.append(sent)
        token_count += sent_tokens
    
    if buf:
        yield _flush(buf, seg, meta)





# Entry Point
def run(json_path: pathlib.Path) -> pd.DataFrame:
    """Convert one *_cleaned.json* file to a DataFrame of chunks."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    meta = {
        "candidate": data.get("candidate"),
        "video_id": data.get("video_id"),
        "url": data.get("url"),
    }


    if meta["candidate"] is None:
        role = data["segments"][0].get("role", "")
        if role.startswith("candidate_"):
            meta["candidate"] = role.replace("candidate_", "").replace("_", " ").title()
        else:
            meta["candidate"] = json_path.stem.split("__")[0].replace("_", " ").title()

    if meta["video_id"] is None:
        parts = json_path.stem.split("__")
        if len(parts) >= 2:
            meta["video_id"] = parts[1]

    meta = {k: v for k, v in meta.items() if v is not None}


    rows: List[Dict[str, Any]] = []
    for seg in data["segments"]:
        rows.extend(chunk_segment(seg, meta))
    return pd.DataFrame(rows)



if __name__ == "__main__":
    if len(sys.argv) not in (2,3):
        sys.exit(
            "Usage:\n"
            "  python -m aipe_ingest.chunker path/to/file_cleaned.json "
            "[huggingface_model_name]"
        )

    json_file = pathlib.Path(sys.argv[1])
    if len(sys.argv) == 3:
        TOKENIZER = get_tokenizer(sys.argv[2])
    
    df = run(json_file)
    out = json_file.with_suffix(".parquet").with_name("chunks.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)


    print(f"Wrote {len(df):,} chunks → {out}")

