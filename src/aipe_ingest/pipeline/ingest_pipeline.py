from pathlib import Path
import os, pandas as pd
from dotenv import load_dotenv

from aipe_common.logger    import get_logger
from aipe_ingest.components.audio_downloader import AudioDownloader
from aipe_ingest.components.transcriber      import WhisperXTranscriber
from aipe_ingest.utils                    import save_as_json
from aipe_ingest.utils                  import load_candidate_interviews
from aipe_ingest.config import RAW_DIR, PROC_DIR, CSV_SOURCES 


log = get_logger(__name__)
load_dotenv()

class IngestPipeline:
    """End-to-end audio → diarised JSON."""

    def __init__(self):
        ffmpeg_path = os.getenv("FFMPEG_PATH", "C:/ffmpeg/bin")
        self.downloader = AudioDownloader(
            ffmpeg_path=ffmpeg_path,
            output_dir=Path("datasets/raw/audio"),
        )
        self.transcriber = WhisperXTranscriber(
            model_name="medium",
            language="es",
            hf_token=os.getenv("HF_AUTH_TOKEN"),
        )
        self.out_dir = RAW_DIR / "output"
        self.out_dir.mkdir(parents=True, exist_ok=True)


    def run(self, skip_existing: bool = True):
        meta = pd.DataFrame(load_candidate_interviews())
        for _, row in meta.iterrows():
            file_base = row["file_base"]
            out_json  = self.out_dir / f"{file_base}.json"

            if skip_existing and out_json.exists():
                log.info("Skipping %s (already done)", file_base)
                continue

            audio = self.downloader.fetch(row["youtube_link"], file_base)
            result = self.transcriber.transcribe(audio, row["youtube_link"])
            save_as_json(result, out_json)
            log.info("Saved → %s", out_json)
