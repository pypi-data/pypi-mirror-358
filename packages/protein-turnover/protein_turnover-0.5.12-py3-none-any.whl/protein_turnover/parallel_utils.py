from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from concurrent.futures import as_completed
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Callable
from typing import Iterator
from typing import Sequence
from typing import TypeVar

import numpy as np
import pandas as pd

from .utils import MzMLResourceFile
from .utils import PeptideSettings

Result = TypeVar("Result")


def get_processpool(workers: int) -> ProcessPoolExecutor:
    return ProcessPoolExecutor(max_workers=workers)


def parallel_result(
    exe: list[Callable[[], Result]],
    workers: int = 4,
) -> Iterator[Result]:
    if not exe:
        return
    nworkers = min(len(exe), workers)
    if nworkers <= 1:
        for e in exe:
            yield e()
        return
    with get_processpool(workers) as executor:
        futures = [executor.submit(e) for e in exe]
        for future in as_completed(futures):
            yield future.result()


def apply_func(series: pd.Series, func: Callable[..., Result]) -> pd.Series:
    return series.apply(func)


def parallel_apply(
    series: pd.Series,
    func: Callable[..., Result],
    workers: int,
) -> pd.Series:
    from functools import partial

    chunk_num = max(len(series) // workers, 1)
    dfs: list[Callable[[], pd.Series]]
    if chunk_num > 1:
        dfs = [
            partial(apply_func, sdf, func) for sdf in np.array_split(series, chunk_num)
        ]
    else:
        dfs = [partial(apply_func, series, func)]
    return pd.concat(
        list(parallel_result(dfs, workers)),
        axis=0,
        ignore_index=False,
    )


@dataclass
class TaskBase:
    pepxml_df: pd.DataFrame
    mzml: MzMLResourceFile
    settings: PeptideSettings
    level: int = 0
    number_of_bg_processes: int = 1

    def mem(self) -> int:
        return self.pepxml_df.memory_usage(deep=True).sum()


class Task(TaskBase, ABC):
    @abstractmethod
    def task_run(self) -> pd.DataFrame: ...


def parallel_tasks(
    tasks: Sequence[Task],
    *,
    workers: int = 4,
) -> Iterator[tuple[pd.DataFrame, MzMLResourceFile]]:
    if not tasks:
        return

    if workers <= 1 or len(tasks) == 1:
        for task in tasks:
            yield task.task_run(), task.mzml
        return
    # ProcessPoolExecutor re-intialize loggers in the worker processes
    # with initialize function?
    nworkers = min(len(tasks), workers)

    with get_processpool(nworkers) as executor:
        futures = {executor.submit(t.task_run): t for t in tasks}
        for future in as_completed(futures):
            yield future.result(), futures[future].mzml
