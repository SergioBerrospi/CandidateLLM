from pathlib import Path
import torch
import whisperx

from aipe_common.logger import get_logger
from aipe_common.exception import TranscriptionError

log = get_logger(__name__)

class WhisperXTranscriber:
    """
    Wraps WhisperX → alignment → diarization in one method.

    Parameters
    ----------
    model_name : str-   WhisperX model (eg. "base", "medium").
    language   : str-   ISO-639-1 language code passed to WhisperX & align model.
    """

    def __init__(self, model_name:str ="medium", language: str = "es", hf_token: str | None = None):
        self.device   = "cuda" if torch.cuda.is_available() else "cpu"
        self.language = language
        self.hf_token = hf_token
        self.model    = whisperx.load_model(model_name, device=self.device)

    def transcribe(self, audio_path:Path, video_url: str) -> dict:
        """Return WhisperX JSON with speaker labels."""
        try:
            log.info("Transcribing %s", audio_path)
            audio = whisperx.load_audio(audio_path)
            result = self.model.transcribe(audio, language = self.language)

            try: 
                model_a, meta = whisperx.load_align_model(
                    language_code=self.language, device=self.device
                )
                result_aligned = whisperx.align(
                    result["segments"], model_a, meta, audio, device=self.device
                )
            except Exception as e:
                log.warning("Alignment failed for %s - %s", video_url, e)
                result_aligned = {'segments': result["segments"]}


            # Diarization
            diarize_model   = whisperx.diarize.DiarizationPipeline(
                use_auth_token=self.hf_token, device=self.device
            )
            diarized_segs = diarize_model(audio)
            final = whisperx.assign_word_speakers(diarized_segs, result_aligned)

            return final
        except Exception as exc:
            raise TranscriptionError(f"Whisperx failed for {audio_path}") from exc