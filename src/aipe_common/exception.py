"""
Centralised exception hierarchy and pretty-traceback helper.

Example
-------
    from aipe_common.exception import (
        error_message_detail, AIPEError, AudioDownloadError
    )

    try:
        risky_call()
    except Exception as exc:
        log.error(error_message_detail(exc))
        raise AudioDownloadError("Cannot download audio") from exc
"""
from __future__ import annotations

import sys
from types import TracebackType

from aipe_common.logger import get_logger

log = get_logger(__name__)

def error_message_detail(exc: Exception) -> str:
    """Return `[file:line] ExceptionType: message` for the active traceback."""
    exc_type, _, exc_tb = sys.exc_info()
    if exc_tb is None:  
        return str(exc)

    while exc_tb.tb_next:
        exc_tb = exc_tb.tb_next

    filename: str = exc_tb.tb_frame.f_code.co_filename
    lineno: int = exc_tb.tb_lineno
    return f"[{filename}:{lineno}] {exc_type.__name__}: {exc}"
