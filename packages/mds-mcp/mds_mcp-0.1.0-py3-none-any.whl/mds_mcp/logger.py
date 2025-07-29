import logging
import os
from typing import Any, MutableMapping, cast

from colorama import Fore, Style, init

init(autoreset=True)

LEVEL_COLORS = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        orig_level = record.levelname
        color = LEVEL_COLORS.get(orig_level, "")
        record.levelname = f"{color}{orig_level}{Style.RESET_ALL}"
        formatted = super().format(record)
        record.levelname = orig_level
        return formatted


class StackLoggerAdapter(logging.LoggerAdapter):
    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        kwargs.setdefault("stacklevel", 1)
        return msg, kwargs


def setup_logger(
    name: str = "model-cache-server",
    log_dir: str = "logs",
    log_file: str = "model-cache-server.log",
    level: int = logging.DEBUG,
) -> StackLoggerAdapter:
    os.makedirs(log_dir, exist_ok=True)
    path = os.path.join(log_dir, log_file)

    fmt = "%(asctime)s %(levelname)-8s %(message)s - %(filename)s:%(lineno)d"
    datefmt = "%Y-%m-%d %H:%M:%S"

    file_formatter = logging.Formatter(fmt, datefmt)
    console_formatter = ColoredFormatter(fmt, datefmt)

    file_handler = logging.FileHandler(path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = cast(list[logging.Handler], [file_handler, console_handler])
    logger.propagate = False

    shared_handlers = cast(list[logging.Handler], [file_handler, console_handler])
    for uv_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvlg = logging.getLogger(uv_name)
        uvlg.setLevel(level)
        uvlg.handlers = shared_handlers[:]
        uvlg.propagate = False
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = shared_handlers[:]
    root_logger.propagate = False

    return StackLoggerAdapter(logger, {})


if __name__ == "__main__":
    logger = setup_logger()
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
