
"""
Usage
-----
    from aipe_common.logger import get_logger

    log = get_logger(__name__)
    log.info("Something happened")
"""


from pathlib import Path
import logging
import os
from datetime import datetime

LOG_DIR = Path(__file__).resolve().parents[2]/"logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / f"{datetime.now():%Y_%m_%d_%H_%M_%S}.log"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

def get_logger(name: str = __name__) -> logging.Logger:
    """Return a module-scoped logger that reuses the global handlers."""
    return logging.getLogger(name)