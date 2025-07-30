from pathlib import Path

ROOT_DIR     = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT_DIR / "datasets"

# immutable data
RAW_DIR   = DATASETS_DIR / "raw"
PROC_DIR  = DATASETS_DIR / "processed"
META_DIR  = DATASETS_DIR / "metadata"

# Granular paths
RAW_AUDIO_DIR   = RAW_DIR  / "audio"      # MP3 files   
RAW_OUTPUT_DIR  = RAW_DIR  / "output"     # whisperx JSON
PROC_CLEAN_DIR  = PROC_DIR / "cleaned"    # *_cleaned.json

CSV_SOURCES = META_DIR / "interview_sources.csv"
CSV_DIARIZE = META_DIR / "interview_diarize.csv"
