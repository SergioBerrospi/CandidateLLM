import json
from pathlib import Path
import typing as t

import pandas as pd
from aipe_common.logger import get_logger
from aipe_common.exception import DataValidationError
from aipe_ingest.utils import slugify

log = get_logger(__name__)


class TranscriptCleaner:
    """
    Relabel speakers (candidate vs interviewer vs other) and write
    `<stem>_cleaned.json` beside / into `clean_dir`.

    Expected CSV columns:
        json_file_name, speaker_candidate, interviewer_1, interviewer_2, ...
    """

    def __init__(
        self,
        raw_json_dir: Path,
        csv_path: Path,
        clean_dir: Path,
    ):
        self.raw_dir   = raw_json_dir
        self.csv_path  = csv_path
        self.clean_dir = clean_dir
        self.clean_dir.mkdir(parents=True, exist_ok=True)

        self.meta = pd.read_csv(self.csv_path)

    def run(self) -> None:
        """Process every row in the CSV → write *_cleaned.json."""
        for _, row in self.meta.iterrows():
            self._clean_one(row)

    def _clean_one(self, row: pd.Series) -> None:
        j_path = self.raw_dir / row["json_file_name"]
        if not j_path.exists():
            log.warning("JSON not found: %s", j_path)
            return

        try:
            transcript = json.loads(j_path.read_text(encoding="utf8"))
        except Exception as exc:
            raise DataValidationError(f"Bad JSON: {j_path}") from exc

        mapping = self._build_mapping(row)
        for seg in transcript.get("segments", []):
            seg["role"] = mapping.get(str(seg.get("speaker")), "other")

        out_path = self.clean_dir / f"{j_path.stem}_cleaned.json"
        out_path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2))
        log.info("Cleaned transcript → %s", out_path)

    @staticmethod
    def _build_mapping(row: pd.Series) -> dict[str, str]:
        """
        Build {speaker_id: role_name}.
        Candidate role becomes `candidate_<slug-from-filename>`.
        Every interviewer_n column (non-NaN) maps to `interviewer_n`.
        """
        cand_slug = slugify(row["json_file_name"].split("__", 1)[0])
        mapping: dict[str, str] = {}

        # candidate
        cand_id = str(row.get("speaker_candidate"))
        if cand_id and cand_id.lower() != "nan":
            mapping[cand_id] = f"candidate_{cand_slug}"

        # any interviewer columns
        for col in row.index:
            if col.startswith("interviewer") and pd.notna(row[col]):
                mapping[str(row[col])] = col  # e.g. interviewer_1

        return mapping