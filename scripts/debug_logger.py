from aipe_common.logger import get_logger
from aipe_common.exception import (
    error_message_detail,
    DataValidationError,
)

log = get_logger(__name__)

def risky_division():
    """Deliberately trigger ZeroDivisionError → wrap in DataValidationError."""
    try:
        _ = 1 / 0
    except ZeroDivisionError as exc:
        # pretty traceback goes to the log
        log.error(error_message_detail(exc))
        # raise our domain-specific error, chaining the original one
        raise DataValidationError("Division by zero encountered") from exc

if __name__ == "__main__":
    try:
        risky_division()
    except DataValidationError:
        # swallow so the script ends cleanly
        log.info("Caught DataValidationError in main()")
