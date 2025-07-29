from __future__ import annotations

import re
import sys
import tomllib
import unicodedata
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import MISSING
from os.path import commonprefix
from os.path import sep
from pathlib import Path
from typing import Any
from typing import Sequence

import tomli_w

from .utils import MzMLResourceFile
from .utils import PeptideSettings
from .utils import PepXMLResourceFile
from .utils import ProtXMLResourceFile
from .utils import ResourceFiles

try:
    from unidecode import unidecode  # type: ignore
except ImportError:

    def unidecode(string: str, errors: str = "ignore", replace_str: str = "?") -> str:
        return string


WIDE = sys.maxunicode > 0xFFFF  # UCS-4 build of python


def find_prefix(filenames: Sequence[Path]) -> Path:
    prefix = commonprefix([Path(m).absolute() for m in filenames])
    if not prefix.endswith(sep):
        i = prefix.rfind(sep)
        if i > 0:
            prefix = prefix[: i + 1]
    return Path(prefix)


def jobidkey(pepxml: str, protxml: str, mzmlfiles: list[str]) -> str:
    from hashlib import md5

    m = md5()
    m.update(str(Path(pepxml).resolve()).encode("utf-8"))
    m.update(str(Path(protxml).resolve()).encode("utf-8"))
    for s in mzmlfiles:
        m.update(str(Path(s).resolve()).encode("utf-8"))

    return m.hexdigest()


def slugify(s: str, transliterate: bool = True) -> str:
    if not s:
        return s

    if WIDE and transliterate:  # UCS-4 build of python
        s = unidecode(s)
    else:
        s = unicodedata.normalize("NFKD", s)

    slug = s.encode("ascii", "ignore").lower()
    slug = re.sub(b"[^a-z0-9]+", b"-", slug).strip(b"-")
    slug = re.sub(b"[-]+", b"-", slug)
    return slug.decode("ascii")


@dataclass
class TurnoverJob:
    job_name: str
    pepxml: list[str]
    protxml: str
    mzmlfiles: list[str]
    jobid: str = ""
    settings: PeptideSettings = PeptideSettings()
    cache_dir: str | None = None
    email: str | None = None
    status: str | None = None  # pending, started, finished, failed, stopped.
    mzfile_to_run: dict[str, str] | None = None
    match_runNames: bool = False
    auto_generated_jobid: bool = False
    """Match peptides to mzML files via their `spectrum` names"""

    def cache_ok(self) -> bool:
        return len(self.to_resource_files().todo()) == 0

    def get_mzfile_to_run(self) -> dict[str, str]:
        if self.mzfile_to_run is None:
            self.mzfile_to_run = {}
        for mz in self.mzmlfiles:
            pmz = Path(mz)
            if pmz.name not in self.mzfile_to_run:
                self.mzfile_to_run[pmz.name] = pmz.stem
        return self.mzfile_to_run

    @property
    def runNames(self) -> set[str]:
        return set(self.get_mzfile_to_run().values())

    def hash(self) -> str:
        from hashlib import md5

        m = md5()
        m.update(self.settings.hash().encode("utf-8"))
        for pepxml in self.pepxml:
            m.update(str(Path(pepxml).resolve()).encode("utf-8"))
        m.update(str(Path(self.protxml).resolve()).encode("utf-8"))
        for mzml in self.mzmlfiles:
            m.update(str(Path(mzml).resolve()).encode("utf-8"))
        for field in fields(self):
            if field.name in {
                "settings",
                "pepxml",
                "protxml",
                "mzmlfiles",
                "mzfile_to_run",
            }:
                continue
            v = getattr(self, field.name)
            m.update(str(v).encode("utf-8"))
        return m.hexdigest()

    def __hash__(self) -> int:
        return int(self.hash(), 16)

    def save(
        self,
        todir: Path | str | None = None,
        filename: str | None = None,
    ) -> Path:
        outdir = Path(todir or self.cache_dir or ".")
        if not outdir.is_dir():
            outdir.mkdir(exist_ok=True, parents=True)
        if filename is None:
            out = outdir.joinpath(self.jobid + ".toml")
        else:
            if not filename.endswith(".toml"):
                filename += ".toml"
            out = outdir.joinpath(filename)

        return self.save_file(out)

    def save_file(self, out: Path) -> Path:
        mzmlfiles = [Path(m).resolve() for m in self.mzmlfiles]
        prefix = find_prefix(mzmlfiles)

        d = {k: v for k, v in asdict(self).items() if v is not None}

        if "cache_dir" in d:  # might be None
            d["cache_dir"] = str(Path(d["cache_dir"]).expanduser().resolve())

        d["pepxml"] = [str(Path(m).resolve()) for m in self.pepxml]
        d["protxml"] = str(Path(d["protxml"]).resolve())
        d["mzmlfiles"] = [str(f.relative_to(prefix)) for f in mzmlfiles]
        d["mzmlprefix"] = str(Path(prefix).resolve())
        # d["settings"] = asdict(d["settings"])
        # settings = d.pop("settings")
        # d.update(settings)
        if "auto_generated_jobid" in d:
            del d["auto_generated_jobid"]
        with out.open("wb") as fp:
            tomli_w.dump(d, fp)
        return out

    @classmethod
    def safe_jobid(cls, turnover_dict: dict[str, Any], filename: Path) -> str:
        return filename.stem
        # job_name = str(turnover_dict["job_name"])
        # return safe_jobid(job_name, filename)

    @classmethod
    def restore(cls, filename: str | Path) -> TurnoverJob:
        def ensure_list(key: str) -> None:
            if key in turnover_dict:
                r = turnover_dict[key]
                if isinstance(r, str):
                    turnover_dict[key] = [r]

        filename = Path(filename)
        with filename.open("rb") as fp:
            turnover_dict: dict[str, Any] = tomllib.load(fp)
            # just what we want...

            ensure_list("mzmlfiles")
            ensure_list("pepxml")
            if "job_name" not in turnover_dict:
                raise TypeError("please specify a job_name")
            if "jobid" not in turnover_dict:
                turnover_dict["jobid"] = cls.safe_jobid(turnover_dict, filename)
                turnover_dict["auto_generated_jobid"] = True
            if "mzmlprefix" in turnover_dict:
                prefix = Path(turnover_dict.pop("mzmlprefix"))
                turnover_dict["mzmlfiles"] = [
                    str(prefix.joinpath(m)) for m in turnover_dict["mzmlfiles"]
                ]
            if "settings" in turnover_dict:
                settings = turnover_dict["settings"]
                settingsd = {
                    f.name: settings[f.name]
                    for f in fields(PeptideSettings)
                    if f.name in settings
                }
                turnover_dict["settings"] = PeptideSettings(**settingsd)
            else:
                settingsd = {
                    f.name: turnover_dict[f.name]
                    for f in fields(PeptideSettings)
                    if f.name in turnover_dict
                }
                turnover_dict["settings"] = PeptideSettings(**settingsd)
            if "protxml" not in turnover_dict:
                turnover_dict["protxml"] = ""

            missing = {k for k in REQUIRED_FIELDS if k not in turnover_dict}
            if missing:
                s = "" if len(missing) > 1 else ""
                raise ValueError(
                    f"turnover file \"{filename}\" is missing: {', '.join(missing)} value{s}",
                )
            # cleanup
            turnover_dict = {k: v for k, v in turnover_dict.items() if k in ALL_FIELDS}
            return cls(**turnover_dict)

    def verify(self) -> bool:
        from .pymz import verify_run

        return verify_run(self)

    def to_resource_files(self) -> ResourceFiles:
        rf = ResourceFiles(
            [PepXMLResourceFile(m, self.cache_dir) for m in set(self.pepxml)],
            ProtXMLResourceFile(self.protxml, self.cache_dir),
            [MzMLResourceFile(m, self.cache_dir) for m in set(self.mzmlfiles)],
        )
        return rf


ALL_FIELDS = {f.name for f in fields(TurnoverJob)}
REQUIRED_FIELDS = {f.name for f in fields(TurnoverJob) if f.default == MISSING}
