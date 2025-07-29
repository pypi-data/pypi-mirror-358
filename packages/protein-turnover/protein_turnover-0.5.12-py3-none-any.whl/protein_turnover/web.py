from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
from types import ModuleType
from typing import Any
from typing import Callable
from typing import Literal
from typing import TypedDict

import click
import tomli_w
from typing_extensions import NotRequired

from .background import Processing
from .cli import CONFIG


class PopenArgs(TypedDict):
    process_group: NotRequired[int | None]
    creationflags: int
    preexec_fn: Callable[[], None] | None


@dataclass
class Runner:
    name: str
    cmd: list[str]
    directory: str = "."
    env: dict[str, str] | None = None
    showcmd: bool = False
    shell: bool = False
    prevent_sig: bool = False  # prevent Cntrl-C from propagating to child process

    def getenv(self) -> dict[str, str] | None:
        if not self.env:
            return None
        return {**os.environ, **self.env}

    def start(self) -> subprocess.Popen[bytes]:
        if self.showcmd:
            click.secho(" ".join(str(s) for s in self.cmd), fg="blue")

        kwargs = PopenArgs(creationflags=0, preexec_fn=None)
        if self.prevent_sig:
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                if sys.version_info >= (3, 11):
                    kwargs["process_group"] = 0
                else:
                    kwargs["preexec_fn"] = os.setpgrp
        return subprocess.Popen(  # type: ignore
            self.cmd,
            cwd=self.directory,
            env=self.getenv(),
            shell=self.shell,
            **kwargs,
        )


def browser(url: str = "http://127.0.0.1:8000", sleep: float = 5.0) -> Thread:
    import webbrowser

    def run() -> None:
        time.sleep(sleep)
        webbrowser.open_new_tab(url)

    tr = Thread(target=run)
    tr.daemon = True  # exit when main process exits
    tr.start()
    return tr


def has_package(package: str) -> bool:
    return get_package(package) is not None


def get_package(package: str) -> ModuleType | None:
    import importlib

    try:
        return importlib.import_module(package)

    except ModuleNotFoundError:
        return None


def has_website() -> bool:
    return has_package("protein_turnover_website")


def default_conf() -> dict[str, Any]:
    # from tempfile import gettempdir

    conf = {
        "MOUNTPOINTS": [
            ("~", "HOME"),
        ],
        "JOBSDIR": "~/turnover_jobs",
        "CACHEDIR": "~/turnover_cache",
        "WEBSITE_STATE": "single_user",
    }
    return conf


def instance_conf(config: Path | str, ns: str | None = None) -> dict[str, Any]:
    # """We *must* have flask in our environment by now"""
    # from flask import Config  # pylint: disable=import-error
    # conf = Config(".")
    # conf.from_pyfile(config)
    # return conf
    try:
        with open(config, "rb") as fp:
            ret = tomllib.load(fp)
            if ns is not None:
                ret2 = ret.get(ns, None)
                return ret2 or {}
            return ret
    except tomllib.TOMLDecodeError as e:
        raise click.BadParameter(
            f'Can\'t parse configuration file "{config}": {e}',
        ) from e


def dump_config(configfile: Path, with_website: bool) -> None:
    from . import config

    def mod2dict(module: ModuleType) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for k in dir(module):
            if k.isupper():
                a = getattr(module, k)
                if a is None:
                    # a = ""
                    continue
                d[k] = a

        d = dict(sorted(d.items()))
        return d

    HEADER = b"""# turnover configuration file.
# Remove/comment out any values you don't change since these are defaults.
"""
    d = mod2dict(config)
    if with_website:
        c = get_package("protein_turnover_website.config")
        assert c is not None
        d["website"] = mod2dict(c)

    click.secho(f"writing {configfile}")
    with open(configfile, "wb") as fp:
        fp.write(HEADER)
        tomli_w.dump(d, fp)


def waitress_app(wsgi_app: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "waitress",
        f"--listen=127.0.0.1:{port}",
        wsgi_app + ":application",
    ]


def flask_app(wsgi_app: str, port: int) -> list[str]:
    return [sys.executable, "-m", "flask", "--app", wsgi_app, "run", f"--port={port}"]


def gunicorn_app(wsgi_app: str, port: int) -> list[str]:
    return [
        sys.executable,
        "-m",
        "gunicorn",
        f"--bind=127.0.0.1:{port}",
        wsgi_app,
    ]


APPS = {"gunicorn": gunicorn_app, "waitress": waitress_app, "flask": flask_app}

WebServer = Literal["flask", "gunicorn", "waitress"]


def webrunner(  # noqa: C901
    *,
    browse: bool,
    workers: int,
    web_config: str | Path | None = None,  # from --web-config
    server: WebServer | None = None,
    view_only: bool = True,
    configfile: str | Path | None = None,  # turnover config file
    defaults: dict[str, Any] | None = None,  # CACHEDIR etc. from commandline
    port: int = 8000,
    server_options: tuple[str, ...] = (),  # extra commandline arguments after --
    wsgi_app: str = "protein_turnover_website.wsgi",
    page: str | None = None,
    email: bool = False,
) -> None:
    """Run full website."""
    from .config import MAIL_SERVER

    if not has_package("protein_turnover_website"):
        click.secho(
            "Please install protein_turnover_website [pip install protein-turnover-website]!",
            fg="red",
            err=True,
        )
        raise click.Abort()
    if server is None:  # try for a better server
        s: WebServer
        for s in ["gunicorn", "waitress", "flask"]:  # type: ignore
            if has_package(s):
                server = s
                break
    else:
        if not has_package(server):
            click.secho(
                f"Please install {server} [pip install {server}]!",
                fg="red",
                err=True,
            )
            raise click.Abort()
    assert server is not None
    if web_config is None:
        if CONFIG.exists():
            web_config = CONFIG
    fp = None
    web_conf = default_conf()
    if MAIL_SERVER and email:
        web_conf["MAIL_SERVER"] = MAIL_SERVER

    if web_config:
        # just need JOBSDIR
        web_conf.update(
            instance_conf(web_config, ns="website"),
        )
    # from commandline so... last
    if defaults is not None:
        web_conf.update(defaults)

    # if web_config and not configfile:
    #     configfile = web_config

    # need to read config file just for jobsdir
    jobsdir = Path(web_conf["JOBSDIR"]).expanduser()
    if not jobsdir.exists():
        jobsdir.mkdir(parents=True, exist_ok=True)
    background = None
    if not view_only:
        email_args = [] if email and MAIL_SERVER else ["--no-email"]
        cfg = [f"--config={configfile}"] if configfile is not None else []
        background = Runner(
            "background",
            [
                sys.executable,
                "-m",
                "protein_turnover",
                *cfg,
                "--level=info",
                "background",
                f"--workers={workers}",
                *email_args,
                str(jobsdir),
            ],
            directory=".",
            prevent_sig=True,
        )
    Url = f"127.0.0.1:{port}"
    if page is not None:
        Url += f"/{page}"

    if sys.platform == "win32":
        KILLSIG = signal.CTRL_C_EVENT
    else:
        KILLSIG = signal.SIGINT
    # ON windows NamedTemporaryFile can't be read
    # by other processes....
    with TemporaryDirectory() as td:
        filename = Path(td) / "turnover-web.cfg"
        with filename.open("wb") as fp:
            tomli_w.dump(web_conf, fp)  # type: ignore

        website = Runner(
            server,
            [
                *APPS[server](wsgi_app, port),
                *server_options,
            ],
            env={"TURNOVER_SETTINGS": str(filename), "FLASK_DEBUG": "0"},
            prevent_sig=True,
        )

        if view_only:
            procs = [website]
        else:
            assert background is not None
            procs = [background, website]

        processes = [(p.name, p.start()) for p in procs]

        if browse:
            browser(url=f"http://{Url}", sleep=5.0)

        worker = Processing(jobsdir)
        ninterrupts = 0
        prev = datetime.now()
        while True:
            try:
                time.sleep(10.0)
                failed = False
                for n, tr in processes:
                    try:
                        retcode = tr.wait(1.0)
                        if retcode != 0:
                            click.echo(f"process failed {n}")
                            failed = True
                    except subprocess.TimeoutExpired:
                        pass
                if failed:
                    raise KeyboardInterrupt()

            except KeyboardInterrupt:
                # too long between ^C
                now = datetime.now()
                if (
                    ninterrupts > 0
                    and not view_only
                    and (now - prev).total_seconds() > 5
                ):
                    ninterrupts = 0
                    prev = now
                    continue
                ninterrupts += 1
                if ninterrupts >= 2 or view_only:
                    for name, tr in processes:
                        click.secho(f"terminating... {name}", fg="blue")
                        tr.send_signal(KILLSIG)
                    for name, tr in processes:
                        try:
                            tr.wait(timeout=4.0)
                        except (OSError, subprocess.TimeoutExpired):
                            pass
                    sys.exit(os.EX_OK)

                prev = now

                if not view_only and worker.is_processing():
                    click.secho(
                        "Warning! The background process is running a job!",
                        fg="yellow",
                        bold=True,
                    )
                click.secho("interrupt... ^C again to terminate")

        # os.system("stty sane")
