from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING
from typing import TypeVar

if TYPE_CHECKING:
    from typing import Iterator

Result = TypeVar("Result")

logger = logging.getLogger("protein_turnover")


def init_logger(
    *,
    level: str | int = logging.INFO,
    logfile: Path | str | None = None,
    reinit: bool = False,
) -> None:
    from .config import LOG_FORMAT

    h: logging.Handler

    if isinstance(level, str):
        level = level.upper()

    def add_handler(h: logging.Handler) -> None:
        fmt = logging.Formatter(LOG_FORMAT)
        h.setFormatter(fmt)
        logger.addHandler(h)

    logger.setLevel(level)
    if reinit:
        for h in list(logger.handlers):
            logger.removeHandler(h)

    if not logger.hasHandlers():
        if logfile is None or logfile == "-":
            add_handler(logging.StreamHandler())
        else:
            add_handler(logging.FileHandler(str(logfile), mode="w"))


def log_iterator(
    it: Iterator[Result],
    *,
    total: int,
    desc: str,
    level: int = 1,
    number_of_bg_processes: int = 1,
) -> Iterator[Result]:
    n = max(1, total // 100)
    if number_of_bg_processes == 1:
        fmt = f"{desc}: [%d/%d %d%%]"
    else:
        fmt = f"{desc}[{level}/{number_of_bg_processes}]: [%d/%d %d%%]"

    for idx, i in enumerate(it, start=1):
        yield i
        if (idx % n) == 0:
            pct = int(idx * 100 / total)
            logger.info(fmt, idx, total, pct)
    logger.info(fmt, total, total, 100)
