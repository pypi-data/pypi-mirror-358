from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import tomllib
from datetime import datetime
from os import walk
from os.path import join
from pathlib import Path
from shutil import which
from typing import Any
from typing import Iterator

import tomli_w

from .logger import logger

try:
    from psutil import pid_exists

    psutil_ok = True
except ImportError:
    psutil_ok = False

    # for windows we need psutil.pid_exists(pid)
    def pid_exists(pid: int) -> bool:
        """Check whether pid exists in the current process table Unix Only."""
        if pid == 0:
            # According to "man 2 kill" PID 0 has a special meaning:
            # it refers to <<every process in the process group of the
            # calling process>> so we don't want to go any further.
            # If we get here it means this UNIX platform *does* have
            # a process with id 0.
            return True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            # EPERM clearly means there's a process to deny access to
            return True
        # According to "man 2 kill" possible error values are
        # (EINVAL, EPERM, ESRCH)
        else:
            return True


# see https://stackoverflow.com/questions/35772001/how-to-handle-a-signal-sigint-on-a-windows-os-machine


# from https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now: bool = False

    def __init__(self) -> None:
        self.kill_now: bool = False
        self.old: Any = None

    def __enter__(self) -> None:
        self.old = signal.signal(signal.SIGTERM, self.exit_gracefully)

    def __exit__(self, *args: Any) -> None:
        if self.old is not None:
            signal.signal(signal.SIGTERM, self.old)
            self.old = None
        if self.kill_now:
            raise ContinueException()

    def exit_gracefully(self, *args: Any) -> None:
        self.kill_now = True


class ContinueException(Exception):
    pass


class Handler:
    def __init__(self, processing: bool = True):
        self.processing = processing

    def __call__(self, signum: int, frame: Any) -> None:
        if self.processing:
            return
        raise ContinueException()

    def arm(self) -> None:
        signal.signal(signal.SIGCONT, self)


class WinHandler(Handler):
    def arm(self) -> None:
        """Don't do anything in Windows"""


PID_FILENAME = "turnover.pid"
PROCESSING = "turnover.pid.is_running"


class Processing:
    """Is the background worker processing a job ATM?"""

    def __init__(self, jobsdir: Path):
        self._processing = jobsdir.joinpath(PROCESSING)

    def is_processing(self) -> bool:
        return self._processing.exists()

    def set_processing(self, start: bool) -> None:
        if start:
            self._processing.touch()
        else:
            try:
                self._processing.unlink(missing_ok=True)
            except OSError:
                pass


class SimpleQueueClient:
    """Used by web client to interact with background Queue.

    Currently only just sends a signal to wake up.
    """

    def __init__(self, jobdir: Path):
        self.jobdir = jobdir
        self.pidfile = jobdir.joinpath(PID_FILENAME)
        if sys.platform == "win32":
            self.KILLSIG = signal.CTRL_C_EVENT
        else:
            self.KILLSIG = signal.SIGINT
        self._iswin = sys.platform == "win32"

    def terminate(self) -> bool:
        pid = self.get_pid()
        if pid is None:
            return False
        try:
            os.kill(pid, self.KILLSIG)
        except ProcessLookupError:
            return False
        except PermissionError:
            return False
        return True

    def signal(self) -> bool:
        pid = self.get_pid()
        if pid is None:
            return False
        try:
            if not self._iswin:
                os.kill(pid, signal.SIGCONT)
        except ProcessLookupError:
            return False
        except PermissionError:
            return False
        return True

    def is_running(self) -> bool:
        pid = self.get_pid()
        if pid is None:
            return False
        return self._pid_exists(pid)

    def get_pid(self) -> int | None:
        if self.pidfile.exists():
            with self.pidfile.open("r") as fp:
                try:
                    return int(fp.read())
                except (TypeError, OSError):
                    return None
        return None

    def _pid_exists(self, pid: int) -> bool:
        return pid_exists(pid)


class SimpleQueue:
    INTERROR = 22

    def __init__(
        self,
        jobdir: str,
        wait: float = 60,
        workers: int = 4,
        nice: int = 0,
        config: str | None = None,
        no_email: bool = False,
    ):
        self.jobdir = jobdir
        self.wait = wait
        self.workers = workers
        self.nice = nice
        self.no_email = no_email
        self.nice_cmd = which("nice")
        self.handler = WinHandler() if sys.platform == "win32" else Handler()
        if config is not None:
            if not os.path.exists(config):
                logger.warning(
                    "configuration file %s doesn't exist! ignoring...",
                    config,
                )
                config = None
        self.config = config
        self.processing = Processing(Path(jobdir))
        if sys.platform == "win32":
            self.KILLSIG = signal.CTRL_C_EVENT
        else:
            self.KILLSIG = signal.SIGINT
        self.handler.arm()

    def command(self, *args: str) -> list[str]:
        nice = []
        if self.nice_cmd and self.nice:
            nice = [self.nice_cmd, "-n", str(self.nice)]

        config = [f"--config={self.config}"] if self.config is not None else []

        no_email = ["--no-email"] if self.no_email else []

        return [
            *nice,
            sys.executable,
            "-m",
            "protein_turnover",
            *config,
            "run",
            f"--interrupt-as-error={self.INTERROR}",
            f"--workers={self.workers}",
            *no_email,
            *args,
        ]

    def pidfile(self, tomlfile: Path) -> Path:
        return tomlfile.parent.joinpath(tomlfile.name + ".pid")

    def rmlog(self, tomlfile: Path) -> None:
        lf = tomlfile.parent.joinpath(tomlfile.stem + ".log")
        lf.unlink(missing_ok=True)

    def runjobs(self, it: Iterator[Path]) -> None:
        for tomlfile in it:
            self.rmlog(tomlfile)

            with subprocess.Popen(
                self.command(str(tomlfile)),
                shell=False,
                text=True,
            ) as proc:
                try:
                    logger.info("%s: running pid=%d", tomlfile, proc.pid)
                    # let website know that this job is running....
                    # see SimpleQueueClient
                    pid = self.pidfile(tomlfile)
                    with pid.open("w") as fp:
                        fp.write(str(proc.pid))
                    self.processing.set_processing(True)
                    try:
                        _, errs = proc.communicate()
                        if errs:
                            logger.error("error from %s: %s", tomlfile, errs)
                        ret = proc.wait()  # TODO what happens when we're terminated?
                    finally:  # can catch KeyboardInterrupt
                        pid.unlink(missing_ok=True)
                        self.processing.set_processing(False)
                    if ret < 0:
                        if -ret in {signal.SIGTERM, signal.SIGKILL}:
                            logger.warning("%s: killed...", tomlfile)
                    status = (
                        "finished"
                        if ret == 0
                        else ("killed" if ret < 0 or ret == self.INTERROR else "failed")
                    )
                    logger.info("%s: status=%s", tomlfile, status)
                    try:
                        self.update_status(tomlfile, status)
                    except Exception as e:
                        logger.error("can't update status! %s: %s", tomlfile, e)
                except KeyboardInterrupt:
                    logger.info("sending signal to child process")
                    proc.send_signal(self.KILLSIG)
                    try:
                        proc.wait(1.0)
                    except subprocess.TimeoutExpired:
                        pass
                    raise

    def update_status(self, tomlfile: Path, status: str) -> None:
        c = self.read_toml(tomlfile)
        if c is None:
            return
        c["status"] = status
        with tomlfile.open("wb") as fp:
            tomli_w.dump(c, fp)

    def read_toml(self, tomlfile: Path) -> dict[str, Any] | None:
        try:
            with tomlfile.open("rb") as fp:
                return tomllib.load(fp)
        except Exception as e:
            logger.error("can't open %s: %s", tomlfile, e)
        return None

    def status(self, tomlfile: Path) -> str:
        c = self.read_toml(tomlfile)
        if c is None:
            return "failed"
        return str(c.get("status", "stopped"))

    def search(self, directory: str, wait: float = 60.0) -> Iterator[Path]:
        nloop = 0
        mtime = None
        todo: list[tuple[Path, datetime]] = []
        every = max(60 * int(60 / wait), 1) if wait else 1  # each hour
        while True:
            if (nloop % every) == 0:
                logger.info("searching for jobs in %s", directory)
            nloop += 1
            for d, _, files in walk(directory):
                for f in files:
                    if f.endswith(".toml"):
                        tomlfile = Path(join(d, f))
                        # already running
                        if self.pidfile(tomlfile).exists():
                            continue
                        mod = datetime.fromtimestamp(tomlfile.stat().st_mtime)
                        if mtime is None or mod > mtime:
                            try:
                                if self.status(tomlfile) == "pending":
                                    todo.append((tomlfile, mod))
                            except (
                                Exception  # pylint: disable=broad-exception-caught
                            ) as e:
                                logger.error("%s: %s", tomlfile, e)

            if todo:
                n = len(todo)
                logger.info("found %d job%s", n, "" if n == 1 else "s")
                todo = sorted(todo, key=lambda t: t[1])  # oldest first
                for tomlfile, m in todo:
                    if tomlfile.exists():
                        mtime = m
                        yield tomlfile
                todo = []
            try:
                # when we are signaled by website with signal.SIGCONT
                # the self.handler will throw a ContinueException
                # but only if processing is False
                # otherwise it will eat the signal
                self.handler.processing = False
                time.sleep(wait)
            except ContinueException:
                # kill -CONT $(cat {pidfile})
                logger.info("awakened by signal....")
            finally:
                self.handler.processing = True

    def process(self, jobdir: str, wait: float = 60.0) -> None:
        self.runjobs(self.search(jobdir, wait))

    def run(self) -> None:
        pidfile = Path(self.jobdir).joinpath(PID_FILENAME)
        try:
            with pidfile.open("wt", encoding="utf-8") as fp:
                pid = os.getpid()
                fp.write(str(pid))
            w = "with 👍" if psutil_ok else "without 👎"
            print(f"protein_turnover queue running ({w} psutil) as pid={pid}")
            self.process(self.jobdir, self.wait)
        finally:
            pidfile.unlink(missing_ok=True)
