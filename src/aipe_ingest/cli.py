"""
AIPE ingestion CLI.

Commands
--------
aipe-ingest fetch   : download audio, transcribe & diarize
aipe-ingest label   : assign candidate / interviewer roles
aipe-ingest prep    : fetch → label (full preprocessing chain)
"""

from pathlib import Path
import typer

from aipe_common.logger import get_logger
from aipe_ingest.pipeline.ingest_pipeline import IngestPipeline
from aipe_ingest.components.postprocessor import TranscriptCleaner
from aipe_ingest.config import (
    RAW_OUTPUT_DIR,  # datasets/raw/output/
    PROC_CLEAN_DIR,  # datasets/processed/cleaned/
    CSV_SOURCES,
)


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
        CSV_SOURCES, help="CSV with candidate / interviewer speaker-IDs"
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


if __name__ == "__main__":
    app()
