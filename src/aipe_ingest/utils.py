
import pandas as pd
import json
import re
from pathlib import Path
from aipe_ingest.config import CSV_SOURCES


def slugify(text):
    """
    Convert text into a slug (e.g., "Exitosa Radio" -> "exitosa_radio").
    """
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

def load_candidate_interviews(csv_path= CSV_SOURCES):
    """
    Load the interview metadata CSV and create a file_base for each entry.
    """
    df = pd.read_csv(csv_path)
    df["file_base"] = df.apply(
        lambda row: f"{row['candidate'].strip()}__{row['date_interview']}__{slugify(row['source'])}", axis=1
    )
    return df.to_dict(orient="records")

def save_as_json(data, path):
    """
    Save a Python object as a JSON file.
    """
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
