from pathlib import Path
import yt_dlp

from aipe_common.logger import get_logger
from aipe_common.exception import AudioDownloadError

log = get_logger(__name__)

class AudioDownloader:
    """
    Download and convert a Youtube video to mp3 file
    """

    def __init__(self, ffmpeg_path:str, output_dir: Path):
        self.ffmpeg_path = ffmpeg_path
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)


    def fetch(self, url:str, file_base:str) -> Path:
        """
        Parameters:
        
        url: str - Youtube link
        file_base: str - Target filename (without extension)

        Returns:
        Path: Absolute path to the '.mp3' file

        """

        out_mp3 = self.output_dir / f"{file_base}.mp3"
        if out_mp3.exists():
            log.info("Audio already on disk --> %s",out_mp3)
            return out_mp3
        
        ydl_opts = {
            "format":"bestaudio/best",
            "ffmpeg_location": self.ffmpeg_path,
            "outtmpl": str(self.output_dir / f"{file_base}.%(ext)s"),
            "postprocessors":[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]

        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(url, download=True)
            log.info("Download %s",url)
            return out_mp3
        
        except Exception as e:
            log.error("Download failed: %s", url, exc_info=True)
            raise AudioDownloadError(url) from e