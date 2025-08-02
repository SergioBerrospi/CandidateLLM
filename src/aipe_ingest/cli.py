"""
AIPE ingestion CLI.

Commands
--------
aipe-ingest fetch   : download audio, transcribe & diarize
aipe-ingest label   : assign candidate / interviewer roles
aipe-ingest prep    : fetch → label (full preprocessing chain)
"""

from pathlib import Path
import typer, pathlib
import pandas as pd
from rich.progress import track  
from aipe_common.logger import get_logger
from aipe_ingest.pipeline.ingest_pipeline import IngestPipeline
from aipe_ingest.components.postprocessor import TranscriptCleaner
from aipe_ingest.config import (
    RAW_OUTPUT_DIR,  # datasets/raw/output/
    PROC_CLEAN_DIR,  # datasets/processed/cleaned/
    CSV_SOURCES,
    CSV_DIARIZE
)
from aipe_ingest.chunker import run as chunk_one


log = get_logger(__name__)
app = typer.Typer(add_completion=False)


@app.command("fetch")
def fetch(
    skip_existing: bool = typer.Option(
        True,
        "--skip-existing/--no-skip-existing",
        help="Skip videos that already have a JSON output",
    ),
):
    """Download from YouTube, then transcribe + diarize with WhisperX."""
    IngestPipeline().run(skip_existing=skip_existing)


@app.command("label")
def label(
    raw_dir: Path = typer.Option(
        RAW_OUTPUT_DIR, help="Folder containing WhisperX JSON files"
    ),
    csv_file: Path = typer.Option(
         CSV_DIARIZE,
         help="CSV (diarize) that has `json_file_name` + speaker IDs",
     ),
    clean_dir: Path = typer.Option(
        PROC_CLEAN_DIR, help="Destination for *_cleaned.json"
    ),
):
    """Re-assign speakers using metadata CSV and write *_cleaned.json."""
    TranscriptCleaner(raw_dir, csv_file, clean_dir).run()


# ---------------------------------------------------------------------- #
@app.command("prep")
def prep(
    skip_existing: bool = typer.Option(
        True, "--skip-existing/--no-skip-existing", help="Forwarded to fetch"
    ),
):
    """Convenience wrapper: **fetch** then **label**."""
    log.info("STEP 1/2 — fetch")
    IngestPipeline().run(skip_existing=skip_existing)

    log.info("STEP 2/2 — label")
    TranscriptCleaner(
        raw_json_dir=RAW_OUTPUT_DIR,
        csv_path=CSV_SOURCES,
        clean_dir=PROC_CLEAN_DIR,
    ).run()

@app.command()
def chunk_all(
    input_dir: pathlib.Path = typer.Option(
        "datasets/processed/cleaned", help="Dir with *_cleaned.json files"
    ),
    output: pathlib.Path = typer.Option(
        "datasets/processed/chunks.parquet", help="Output parquet"
    ),
):
    dfs=[]
    files=list(input_dir.rglob("*_cleaned.json"))
    if not files:
        typer.echo("No '*_cleaned.json' files found")
        raise typer.Exit(1)
    
    for fp in track(files, description="Chunking"):
        dfs.append(chunk_one(fp))

    master = pd.concat(dfs, ignore_index = True)
    output.parent.mkdir(parents=True, exist_ok=True)
    master.to_parquet(output, index=False)
    typer.echo(f"Saved {len(master):,} chunks -->> {output}")



if __name__ == "__main__":
    app()
