from __future__ import annotations

import hashlib
import math
from dataclasses import asdict
from dataclasses import dataclass
from functools import reduce
from pathlib import Path
from typing import Any
from typing import Literal
from typing import TYPE_CHECKING
from typing import TypedDict

import numpy as np
import pandas as pd

from .exts import DINOSAUR
from .exts import EICS
from .exts import EXT
from .exts import MZMAP
from .exts import MZML
from .exts import PEPXML
from .exts import PROTXML
from .exts import RESULT_EXT

if TYPE_CHECKING:
    from .types.pepxmltypes import PepXMLRunRow


@dataclass
class PeptideSettings:
    rtTolerance: float = 15.0  # seconds
    mzTolerance: float = 1e-5
    labelledIsotopeNumber: int = 15
    labelledElement: str = "N"
    maximumLabelEnrichment: float = 0.95
    retentionTimeCorrection: Literal["UseInSample", "SimpleMedian"] = "SimpleMedian"
    useObservedMz: bool = False
    minProbabilityCutoff: float = 0.8
    enrichmentColumns: int = 10
    # fdrMaximum: float = 0.0
    # psmFilters: Filter | None = None

    def __post_init__(self) -> None:
        if self.labelledElement not in ATOMICPROPERTIES:
            raise ValueError(f"unknown element {self.labelledElement}")
        if (
            self.labelledIsotopeNumber
            not in ATOMICPROPERTIES[self.labelledElement]["isotopeNr"]
        ):
            raise ValueError(
                f"unknown isotopeNumber {self.labelledIsotopeNumber} for {self.labelledElement}",
            )

    def hash(self) -> str:
        from hashlib import md5

        m = md5()
        for k, v in asdict(self).items():
            if isinstance(v, float):
                v = round(v, 6)
            m.update(f"{k}={v}".encode())
        return m.hexdigest()

    def __hash__(self) -> int:
        return int(self.hash(), 16)

    @property
    def labelledAtomicAbundancesAtMaxEnrich(self) -> np.ndarray:
        return labelledAtomicAbundancesAtMaxEnrich(self)

    @property
    def iabundance(self) -> int:
        return getIabundance(self)

    @property
    def abundance(self) -> float:
        return getAbundance(self)

    @property
    def naturalAtomicAbundances(self) -> np.ndarray:
        return naturalAtomicAbundances(self.labelledElement)

    def labelledAtomicAbundances(self, abundance: float) -> np.ndarray:
        return labelledAtomicAbundances(
            self.labelledIsotopeNumber,
            self.labelledElement,
            abundance,
        )

    # def getEnrichments(self, peptide: str) -> np.ndarray:
    #     return getEnrichments(peptide, self)

    def getEnrichmentsN(self, ncols: int) -> np.ndarray:
        return getEnrichmentsN(ncols, self)

    def isoMzDiff(self, assumed_charge: int) -> float:
        return isoMzDiff(assumed_charge, self)

    def getElementCount(self, formula: np.ndarray) -> int:
        return getElementCount(formula, self.labelledElement)

    def getElementCountFromPeptide(self, peptide: str) -> int:
        return self.getElementCount(peptideFormula(peptide))

    def eic_mzranges(self, pep: PepXMLRunRow) -> np.ndarray:
        return eic_mzranges(pep, self)


class PeptideInfo:
    def __init__(self, peptide: str, settings: PeptideSettings) -> None:
        self.peptide = peptide
        self.settings = settings
        self._formula: np.ndarray | None = None

    @property
    def formula(self) -> np.ndarray:
        if self._formula is None:
            self._formula = peptideFormula(self.peptide)
        return self._formula

    @property
    def elementCount(self) -> int:
        return self.settings.getElementCount(self.formula)

    def getEnrichments(self, maxIso: int) -> np.ndarray:
        """enrichmentColumns array of enrichments"""
        ncols = self.settings.enrichmentColumns
        if ncols <= 0:
            ncols = self.elementCount
        elif ncols == 1:
            ncols = maxIso + 1  # make it square....
        return self.settings.getEnrichmentsN(ncols)

    @property
    def naturalAtomicAbundances(self) -> np.ndarray:
        return self.settings.naturalAtomicAbundances

    def labelledAtomicAbundances(self, abundance: float) -> np.ndarray:
        return self.settings.labelledAtomicAbundances(abundance)

    @property
    def iabundance(self) -> int:
        return self.settings.iabundance

    @property
    def abundance(self) -> float:
        return self.settings.abundance


NPA = np.array


def NPI(list_of_ints: list[int]) -> np.ndarray[Any, np.dtype[np.int32]]:
    return np.array(list_of_ints, dtype=np.int32)


NAMES = np.array(["C", "H", "O", "N", "P", "S", "Se"])
# "C", "H", "O" ,"N", "P", "S" , "Se"
# minus H20
#   "U": NPI([3,5,1,1,0,0,1])
AMINOACIDS = {
    "A": NPI([3, 5, 1, 1, 0, 0, 0]),
    "C": NPI([3, 5, 1, 1, 0, 1, 0]),
    "D": NPI([4, 5, 3, 1, 0, 0, 0]),
    "E": NPI([5, 7, 3, 1, 0, 0, 0]),
    "F": NPI([9, 9, 1, 1, 0, 0, 0]),
    "G": NPI([2, 3, 1, 1, 0, 0, 0]),
    "H": NPI([6, 7, 1, 3, 0, 0, 0]),
    "I": NPI([6, 11, 1, 1, 0, 0, 0]),
    "K": NPI([6, 12, 1, 2, 0, 0, 0]),
    "L": NPI([6, 11, 1, 1, 0, 0, 0]),
    "M": NPI([5, 9, 1, 1, 0, 1, 0]),
    "N": NPI([4, 6, 2, 2, 0, 0, 0]),
    "P": NPI([5, 7, 1, 1, 0, 0, 0]),
    "Q": NPI([5, 8, 2, 2, 0, 0, 0]),
    "R": NPI([6, 12, 1, 4, 0, 0, 0]),
    "S": NPI([3, 5, 2, 1, 0, 0, 0]),
    "T": NPI([4, 7, 2, 1, 0, 0, 0]),
    "V": NPI([5, 9, 1, 1, 0, 0, 0]),
    "W": NPI([11, 10, 1, 2, 0, 0, 0]),
    "Y": NPI([9, 9, 2, 1, 0, 0, 0]),
    "a": NPI([2, 2, 1, 0, 0, 0, 0]),
    "c": NPI([5, 8, 2, 2, 0, 1, 0]),
    "m": NPI([5, 9, 2, 1, 0, 1, 0]),
    "U": NPI([3, 5, 1, 1, 0, 0, 1]),
}


class AtomicProperties(TypedDict):
    isotopeNr: np.ndarray[Any, np.dtype[np.int32]]
    abundance: np.ndarray[Any, np.dtype[np.float64]]
    mass: np.ndarray[Any, np.dtype[np.float64]]


# WARNING! the zeroth value is assumed to be the "natural" isotope.
ATOMICPROPERTIES: dict[str, AtomicProperties] = dict(
    C=dict(
        isotopeNr=NPI([12, 13]),
        mass=NPA([12.0, 13.0033548378]),
        abundance=NPA([0.9889, 0.0111]),
    ),
    H=dict(
        isotopeNr=NPI([1, 2]),
        mass=NPA([1.0078250321, 2.0141017780]),
        abundance=NPA([0.9998, 0.0001]),
    ),
    O=dict(
        isotopeNr=NPI([16, 17, 18]),
        mass=NPA([15.9949146, 16.9991312, 17.9991603]),
        abundance=NPA([0.9976, 0.0004, 0.0020]),
    ),
    N=dict(
        isotopeNr=NPI([14, 15]),
        mass=NPA([14.0030740052, 15.0001088984]),
        abundance=NPA([0.99633, 0.00367]),
    ),
    # need entry for formula...
    P=dict(isotopeNr=NPI([31]), mass=NPA([30.97376163]), abundance=NPA([1.0])),
    # out of (isotope number) order abundance...
    S=dict(
        isotopeNr=NPI([32, 33, 34, 36]),
        mass=NPA([31.97207070, 32.97145843, 33.96786665, 35.96708062]),
        abundance=NPA([0.9502, 0.0075, 0.0421, 0.0002]),
    ),
    Se=dict(
        isotopeNr=NPI([80, 78, 76, 82, 77, 74]),
        mass=NPA(
            [79.9165213, 77.9173091, 75.9192136, 81.9166994, 76.919914, 73.9224764],
        ),
        abundance=NPA([0.4961, 0.2377, 0.0937, 0.0873, 0.0763, 0.0089]),
    ),
)


def getNr(element: str) -> int:
    """get isotope number for most abundant element"""
    if element not in ATOMICPROPERTIES:
        raise ValueError(f'unknown element: "{element}"')
    at = ATOMICPROPERTIES[element]
    a = at["abundance"]
    return int(at["isotopeNr"][a.argmax()])


def getElementCount(formula: np.ndarray, element: str) -> int:
    return formula[NAMES == element][0]


def okNr(element: str) -> set[int]:
    at = ATOMICPROPERTIES[element]
    a = at["isotopeNr"]
    return {int(i) for i in a}


# return C H O N P S Se count list
def peptideFormula(peptideSequence: str) -> np.ndarray[Any, np.dtype[np.int32]]:
    startComp = NPI([0, 2, 1, 0, 0, 0, 0])
    return reduce(
        lambda total, aa: total + AMINOACIDS[aa],
        list(peptideSequence),
        startComp,
    )


def getIabundance(settings: PeptideSettings) -> int:
    a = ATOMICPROPERTIES[settings.labelledElement]
    b = a["isotopeNr"] == settings.labelledIsotopeNumber
    return np.where(b)[0][0]


def getAbundance(setting: PeptideSettings) -> float:
    a = ATOMICPROPERTIES[setting.labelledElement]
    b = a["isotopeNr"] == setting.labelledIsotopeNumber
    return a["abundance"][b][0]


# def getEnrichments(peptide: str, settings: PeptideSettings) -> np.ndarray:
#     """elementCount + 1 array of enrichments"""

#     # elementCount = settings.getElementCountFromPeptide(peptide)
#     elementCount = settings.enrichmentColumns
#     return getEnrichmentsN(elementCount, settings)


def getEnrichmentsN(elementCount: int, settings: PeptideSettings) -> np.ndarray:
    return np.linspace(
        settings.abundance,
        settings.maximumLabelEnrichment,
        elementCount,
        endpoint=True,
    )
    # de = (settings.maximumLabelEnrichment - naturalLabelledElement) / (elementCount - 1)
    # return np.array(
    #     [naturalLabelledElement + i * de for i in range(elementCount)],
    #     dtype=np.float32,
    # )


def labelledAtomicAbundances(
    labelledIsotopeNumber: int,
    element: str,
    abundance: float,
) -> np.ndarray:
    if element in ATOMICPROPERTIES:
        ap = ATOMICPROPERTIES[element]
        if labelledIsotopeNumber in ap["isotopeNr"]:
            a = ap["abundance"]
            label = ap["isotopeNr"] == labelledIsotopeNumber
            adjustedAbundance: np.ndarray = (1 - abundance) * a / np.sum(a[~label])

            adjustedAbundance[label] = abundance
            return adjustedAbundance
    raise ValueError(f"unknown element {element}[{labelledIsotopeNumber}]")


def naturalAtomicAbundances(
    element: str,
) -> np.ndarray:
    if element in ATOMICPROPERTIES:
        ap = ATOMICPROPERTIES[element]
        return ap["abundance"]

    raise ValueError(f"unknown element: {element}")


def labelledAtomicAbundancesAtMaxEnrich(
    settings: PeptideSettings,
) -> np.ndarray:
    return labelledAtomicAbundances(
        settings.labelledIsotopeNumber,
        settings.labelledElement,
        settings.maximumLabelEnrichment,
    )


def okiso(settings: PeptideSettings) -> bool:
    props = ATOMICPROPERTIES[settings.labelledElement]
    isotopeNr, abundance = props["isotopeNr"], props["abundance"]
    idx = (isotopeNr == settings.labelledIsotopeNumber)[0]
    ab = (abundance == np.max(abundance))[0]
    return idx != ab


def isoMzDiff(assumed_charge: int, settings: PeptideSettings) -> float:
    props = ATOMICPROPERTIES[settings.labelledElement]
    mass, abundance = props["mass"], props["abundance"]
    isoDiff = (
        mass[props["isotopeNr"] == settings.labelledIsotopeNumber]
        - mass[abundance == np.max(abundance)]
    )
    isoMzDiff = isoDiff[0] / assumed_charge
    return isoMzDiff


def eic_mzranges(pep: PepXMLRunRow, settings: PeptideSettings) -> np.ndarray:
    # requires
    # maxIso, mz, assumed_charge and
    # (settings.{labelledElement,labelledIsotopeNumber}, mzTolerance)
    isoDiff = settings.isoMzDiff(pep.assumed_charge)
    mz = pep.observed_mz if settings.useObservedMz else pep.mz
    tol = mz * settings.mzTolerance
    # NOTE: pep.maxIso might be a floating point number if
    # pep is actually a pd.Series
    isoRange = range(-1, round(pep.maxIso) + 1)

    mzranges = [
        [
            mz + iso * isoDiff - tol,
            mz + iso * isoDiff + tol,
        ]
        for iso in isoRange
    ]
    return np.array(mzranges, dtype=np.float32)


def resize(a: np.ndarray, width: int) -> np.ndarray:
    d = width - len(a)
    if d > 0:
        return np.pad(a, (0, d), "constant", constant_values=(0, 0))
    if d < 0:
        return a[:width]
    return a


def ensure_pos(a: np.ndarray) -> np.ndarray:
    # use np.fmax if we want to set a[i] to zero if a[i] is NaN
    return np.maximum(a, 0.0)
    # return np.where(a >= 0, a, 0.0)


def roundit(n: float, nsig: int = 3) -> int:
    from math import log10

    assert n > 0, str(n)
    pwr = round(log10(n))
    pwr = max(0, pwr - nsig)
    num = 10**pwr
    return round(n / num) * num


def human(num: int, suffix: str = "B", scale: int = 1) -> str:
    if not num:
        return f"0{suffix}"
    num *= scale
    magnitude = int(math.floor(math.log(abs(num), 1000)))
    val = num / math.pow(1000, magnitude)
    if magnitude > 7:
        return "{:.1f}{}{}".format(val, "Y", suffix)
    return "{:3.1f}{}{}".format(
        val,
        ["", "k", "M", "G", "T", "P", "E", "Z"][magnitude],
        suffix,
    )


def hash256(filename: Path, bufsize: int = 4096 * 8, algo: str = "sha256") -> str:
    sha256_hash = hashlib.new(algo, usedforsecurity=False)
    with filename.open("rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(bufsize), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def fileok(cached: list[Path], original: Path) -> bool:
    if not cached:
        return False
    if not original.is_file():
        return False
    omtime = original.stat().st_mtime
    for cache in cached:
        if not cache.is_file() or omtime > cache.stat().st_mtime:
            return False
    return True


class BaseResourceFile:
    def __init__(
        self,
        original: Path | str,
        cache_dir: Path | str | None = None,
    ):
        self.original = Path(original).expanduser().resolve()
        if cache_dir is None:
            self.cache_dir = self.original.parent
        else:
            self.cache_dir = Path(cache_dir).expanduser().resolve()
        self._hash: str | None = None

    @property
    def name(self) -> str:
        return self.original.name

    @property
    def exists(self) -> bool:
        return self.original.exists()

    def extok(self, *ext: str) -> bool:
        targets = [self.cache_file(e) for e in ext]
        return fileok(targets, self.original)

    def cache_file(self, ext: str) -> Path:
        # return self.cache_dir.joinpath(self.name + ext)
        return self.cache_dir.joinpath(self.hash + ext)

    def touch(self) -> bool:
        return False

    def cache_ok(self) -> bool:
        return False

    @property
    def hash(self) -> str:
        if self._hash is not None:
            return self._hash

        self._hash = self.get_hash()
        return self._hash

    def get_hash(self) -> str:
        return hash256(self.original)

    def cleanup(self) -> None:
        for pth in self.all_cache_files():
            try:
                pth.unlink(missing_ok=True)
            except OSError:
                pass

    def all_cache_files(self) -> list[Path]:
        return []


class MzMLResourceFile(BaseResourceFile):
    @property
    def runName(self) -> str:
        """Name possibly in pep.xml file as <spectrum_query spectrum="{runName}.{start_scan}.{end_scan}.0 ...>"""
        return self.original.stem

    def cache_mzml(self) -> Path:
        return self.cache_file(MZML)

    def cache_memmap(self) -> Path:
        return self.cache_file(MZMAP)

    def cache_dinosaur(self) -> Path:
        return self.cache_file(DINOSAUR)

    def cache_mzml_ok(self) -> bool:
        from .dinosaur.dinosaur import DinoRunner

        ok = self.extok(MZMAP, MZML)
        if not ok:
            return False
        ok = self.extok(DINOSAUR)
        if ok:
            return True

        dino = DinoRunner.from_config()
        # no dino file check if we can generate it...
        if dino is not None and dino.can_run():
            return False
        # ok we can't generate it so cache is "fine..."
        return True

    def cache_ok(self) -> bool:
        return self.cache_mzml_ok()

    def touch(self) -> bool:
        if self.cache_ok():
            self.cache_memmap().touch()
            self.cache_mzml().touch()
            return True
        return False

    def all_cache_files(self) -> list[Path]:
        return [self.cache_mzml(), self.cache_memmap()]


class MzMLResourceFileLocal(MzMLResourceFile):
    def __init__(
        self,
        original: Path | str,
        directory: Path | str | None = None,
        name: str | None = None,
    ):
        super().__init__(original, directory)
        if name is None:
            name = self.runName
        self.outname = name

    def cache_file(self, ext: str) -> Path:
        # return self.cache_dir.joinpath(self.name + ext)
        return self.cache_dir.joinpath(self.outname + ext)

    def cache_mzml(self) -> Path:
        return self.cache_file("." + EXT)

    def cache_memmap(self) -> Path:
        return self.cache_file(".mzi")

    def cache_mzml_ok(self) -> bool:
        return self.extok("." + EXT, ".mzi")


class PepXMLResourceFile(BaseResourceFile):
    def cache_pepxml(self) -> Path:
        return self.cache_file(PEPXML)

    def cache_pepxml_ok(self) -> bool:
        return self.extok(PEPXML)

    def cache_ok(self) -> bool:
        return self.cache_pepxml_ok()

    def touch(self) -> bool:
        if self.cache_ok():
            self.cache_pepxml().touch()
            return True
        return False

    def all_cache_files(self) -> list[Path]:
        return [self.cache_pepxml()]


class ProtXMLResourceFile(BaseResourceFile):
    def cache_protxml(self) -> Path:
        return self.cache_file(PROTXML)

    def cache_protxml_ok(self) -> bool:
        return self.extok(PROTXML)

    def cache_ok(self) -> bool:
        return self.cache_protxml_ok()

    def touch(self) -> bool:
        if self.cache_ok():
            self.cache_protxml().touch()
            return True
        return False

    def all_cache_files(self) -> list[Path]:
        return [self.cache_protxml()]


class ResultsResourceFile(BaseResourceFile):
    def cache_result(self) -> Path:
        return self.cache_file(RESULT_EXT)

    def cache_pepxml(self) -> Path:
        return self.cache_file(PEPXML)

    def cache_envelope(self) -> Path:
        return self.cache_file(EICS)

    def cache_file(self, ext: str) -> Path:
        return self.cache_dir.joinpath(self.original.name + ext)

    def all_cache_files(self) -> list[Path]:
        return [self.cache_result(), self.cache_pepxml(), self.cache_envelope()]

    def has_result(self) -> bool:
        return self.cache_result().exists()


class ResourceFiles:
    def __init__(
        self,
        pepxmls: list[PepXMLResourceFile],
        protxml: ProtXMLResourceFile,
        mzmlfiles: list[MzMLResourceFile],
    ):
        self.pepxmls = pepxmls
        self.protxml = protxml
        self.mzmlfiles = mzmlfiles
        self.cache_dirs = {
            *[s.cache_dir for s in pepxmls],
            *[s.cache_dir for s in mzmlfiles],
        }

    def lock(self, job_id: str) -> None:
        for c in self.cache_dirs:
            c.joinpath(job_id + ".lock").touch()

    def unlock(self, job_id: str) -> None:
        for c in self.cache_dirs:
            c.joinpath(job_id + ".lock").unlink(missing_ok=True)  # type: ignore

    def is_locked(self) -> bool:
        return len([f for c in self.cache_dirs for f in c.glob("*.lock")]) > 0

    def todo(self) -> list[BaseResourceFile]:
        ret: list[BaseResourceFile] = []
        for pepxml in self.pepxmls:
            if not pepxml.cache_pepxml_ok():
                ret.append(pepxml)
        for mzml in self.mzmlfiles:
            if not mzml.cache_mzml_ok():
                ret.append(mzml)
        return ret

    def ensure_directories(self) -> None:
        for cd in self.cache_dirs:
            if not cd.is_dir():
                cd.mkdir(parents=True, exist_ok=True)


def rmfiles(files: list[Path]) -> None:
    from contextlib import suppress

    for f in files:
        with suppress(OSError):
            Path(f).unlink()


def rehydrate_turnover(turn: pd.DataFrame) -> pd.DataFrame:
    if "modifications" in turn.columns and "modcol" not in turn.columns:
        turn["modcol"] = turn["modifications"].apply(Apply.modcol)
    if "eics" in turn.columns and "eics_shape" in turn.columns:
        turn["eics"] = turn[["eics", "eics_shape"]].apply(
            Apply.eics_reshape,
            axis=1,
        )
        turn.drop(columns=["eics_shape"], inplace=True)
    if "mzranges" in turn.columns:
        turn["mzranges"] = turn["mzranges"].apply(lambda mz: mz.reshape((-1, 2)))
    if "isotopeRegressions" in turn.columns:
        turn["isotopeRegressions"] = turn["isotopeRegressions"].apply(
            lambda mz: mz.reshape((-1, 2)),
        )
    return turn


# def read_rds(filename: str) -> pd.DataFrame:
#     df = IO(filename).read_df()
#     df = rehydrate_turnover(df)
#     return df


def duplicate_rows(df: pd.DataFrame, on: list[str]) -> pd.DataFrame:
    return df[df.duplicated(on, keep=False)]


def fdr(df: pd.DataFrame) -> float:
    decoy = df["is_decoy"].sum()
    denom = len(df) - decoy
    return float(decoy) / denom if denom > 0 else np.inf


def calculate_fdrs(
    df: pd.DataFrame,
    nbins: int = 50,
    score: str = "peptideprophet_probability",
) -> pd.Series:
    """Requires peptideprophet_probability, is_decoy"""
    # df['fdr'] = calculate_fdrs(df)
    from math import ceil

    decoys = df["is_decoy"]
    pbins = df[score].apply(lambda p: ceil(p * nbins))

    mx = int(pbins.max())

    fdrs: dict[int, float] = {}
    for binno in range(mx + 1):
        target = pbins >= binno
        n = target.sum()
        if n == 0:
            fdrs[binno] = fdrs.get(binno - 1, 0.0)
            continue
        ndecoys = decoys[target].sum()
        denom = n - ndecoys
        fdrs[binno] = ndecoys / denom if denom > 0 else np.inf
    return pbins.apply(lambda binno: fdrs[binno]).astype(np.float32)


class Apply:
    @staticmethod
    def eics_reshape(s: pd.Series) -> np.ndarray:
        return s["eics"].reshape(s["eics_shape"])

    @staticmethod
    def eics_reshape_np(s: pd.Series) -> np.ndarray:
        return np.array(s["eics"]).reshape(s["eics_shape"])

    @staticmethod
    def modcol(mods: list[dict], n: int = 3) -> str:
        mods = sorted(mods, key=lambda d: d["position"])
        return ":".join([f"{d['mass']:.{n}f}@{d['position']}" for d in mods])

    @staticmethod
    def binrt(rt: float, rttol: float = 15.0) -> int:
        return round(rt / rttol)

    @staticmethod
    def binmz(mz: float, mztol: float = 10e-6) -> int:
        return round(mz / mztol)


class IO:
    def __init__(self, filename: Path | str, df: pd.DataFrame | None = None):
        self.df = df
        self.filename = Path(filename)

    def save_df(self, index: bool = False) -> None:
        assert self.df is not None
        try:
            self.df.to_parquet(self.filename, index=index)

        except (Exception, KeyboardInterrupt):
            rmfiles([self.filename])  # cleanup
            raise

    def read_df(self, columns: list[str] | None = None) -> pd.DataFrame:
        if self.filename.name.endswith(".feather"):
            return pd.read_feather(self.filename, columns=columns, use_threads=True)
        return pd.read_parquet(self.filename, columns=columns, use_threads=True)


def df_can_write(fmt: str) -> bool:
    from io import BytesIO

    df = pd.DataFrame({"x", [0]})  # pylint: disable=unhashable-member
    func = getattr(df, f"to_{fmt}", None)
    if func is None:
        return False
    try:
        func(BytesIO())
        return True
    except ModuleNotFoundError:
        return False


def df_can_write_parquet() -> bool:
    return df_can_write("parquet")


def df_can_write_excel() -> bool:
    return df_can_write("excel")


def getsize(fname: Path) -> int:
    return fname.stat().st_size
