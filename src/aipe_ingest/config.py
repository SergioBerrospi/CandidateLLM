from pathlib import Path

# Top-level folders
ROOT_DIR     = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT_DIR / "datasets"

RAW_DIR   = DATASETS_DIR / "raw"
PROC_DIR  = DATASETS_DIR / "processed"
META_DIR  = DATASETS_DIR / "metadata"         # ← CHANGED (new constant)

# Metadata CSVs
CSV_SOURCES  = META_DIR / "interview_sources.csv"   # ← CHANGED
CSV_DIARIZE  = META_DIR / "interview_diarize.csv"   # ← CHANGED
