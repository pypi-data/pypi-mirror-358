from __future__ import annotations

import logging
import mmap
import re
from collections import Counter
from os.path import commonprefix
from pathlib import Path
from typing import Callable
from typing import Iterator

import numpy as np
import pandas as pd

from .alt_fit import mk_maxIso
from .jobs import TurnoverJob
from .logger import logger
from .types.pepxmltypes import PepXMLRunRow
from .utils import Apply
from .utils import human
from .utils import IO
from .utils import PeptideSettings
from .utils import PepXMLResourceFile


def chop_spectrum(spectrum: str) -> str:
    ret = ".".join(spectrum.split(".")[:-3])
    return ret


def bchop_spectrum(spectrum: bytes) -> bytes:
    ret = b".".join(spectrum.split(b".")[:-3])
    return ret


SPECTRUM = re.compile(b'spectrum="([^"]+)"')


def count_spectra(pepxml: Path) -> dict[str, int]:
    """Very fast inspection of pep.xml spectra names"""
    cnt: dict[bytes, int] = Counter()
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in SPECTRUM.finditer(mm):
                spectrum = bchop_spectrum(m.group(1))
                cnt[spectrum] += 1

    return {k.decode("ascii"): v for k, v in cnt.items()}


SPECTRUM_QUERY = re.compile(b"<spectrum_query ")


def scan_spectra(pepxml: Path) -> Iterator[int]:
    """Very fast inspection of pep.xml spectra queries"""
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for m in SPECTRUM_QUERY.finditer(mm):
                yield m.start(0)


PEPTIDE_PROPHET_QUERY = re.compile(b"<peptideprophet_summary ")


def scan_pp_probability(pepxml: Path) -> bool:
    with pepxml.open("rb") as fp:
        with mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            for _ in PEPTIDE_PROPHET_QUERY.finditer(mm):
                return True
    return False


def fractionExtractorRegexFinder(runNames: list[str]) -> re.Pattern | None:
    if len(runNames) <= 1:
        return None
    prefix = commonprefix(runNames)
    n = len(prefix)
    rev = [f[n:][::-1] for f in runNames]
    postfix = commonprefix(rev)[::-1]
    if n + len(postfix) >= len(min(runNames, key=len)):
        return None
    return re.compile(f"^{re.escape(prefix)}(.*){re.escape(postfix)}$")


def decoy_prefix_fn(prefix: str = "DECOY_") -> Callable[[list[str]], bool]:
    prefix = prefix.lower()
    return lambda proteins: all(p.lower().startswith(prefix) for p in proteins)


def decoy_postfix_fn(postfix: str = "_DECOY") -> Callable[[list[str]], bool]:
    postfix = postfix.lower()
    return lambda proteins: all(p.lower().endswith(postfix) for p in proteins)


def init_agg(
    df: pd.DataFrame,
    decoy_prefix: str = "DECOY_",
    decoy_postfix: str | None = None,
) -> pd.DataFrame:
    from .utils import calculate_fdrs

    decoyfn = (
        decoy_postfix_fn(decoy_postfix)
        if decoy_postfix is not None
        else decoy_prefix_fn(decoy_prefix)
    )
    df["modcol"] = df["modifications"].apply(Apply.modcol)
    df["is_decoy"] = df["proteins"].apply(decoyfn)
    if "fdr" not in df.columns:
        for prob in ["peptideprophet_probability", "probability"]:
            if prob in df.columns:
                df["fdr"] = calculate_fdrs(df, score=prob)
                break
    # Before or after grouping!

    # add H+
    df["observed_mz"] = (
        df["precursor_neutral_mass"] / df["assumed_charge"] + 1.00727646677
    )

    df["mz"] = df["calc_neutral_pep_mass"] / df["assumed_charge"] + 1.00727646677

    return df


def aggregateSearchHits(
    df: pd.DataFrame,
    *,
    settings: PeptideSettings,
    decoy_prefix: str = "DECOY_",
    decoy_postfix: str | None = None,
    runNames: set[str] | None = None,
) -> pd.DataFrame:
    from .config import GROUP_RT

    mztol = settings.mzTolerance
    rttol = settings.mzTolerance
    use_simple_median = settings.retentionTimeCorrection != "UseInSample"

    df = init_agg(
        df,
        decoy_prefix=decoy_prefix,
        decoy_postfix=decoy_postfix,
    )
    if runNames is not None:
        df["isLabelledRun"] = df["run"].apply(lambda r: r in runNames)
        keys = ["run"]
    else:
        df["isLabelledRun"] = False
        keys = []

    df["agg_count"] = 1

    keys.extend(["peptide", "_massint", "assumed_charge", "modcol"])
    df["_massint"] = df["calc_neutral_pep_mass"].apply(lambda m: round(m / mztol))
    remove = ["_massint"]

    if GROUP_RT:
        df["_rtint"] = df["retention_time_sec"].apply(lambda rt: round(rt / rttol))
        keys.append("_rtint")
        remove.append("_rtint")

    # cols = ['spectrum', 'spectrumNativeID', 'precursor_neutral_mass',
    #    'assumed_charge', 'retention_time_sec', 'start_scan', 'end_scan',
    #    'index', 'proteins', 'protein_descr', 'peptide_next_aa',
    #    'peptide_prev_aa', 'num_tol_term', 'xcorr', 'deltacn', 'deltacnstar',
    #    'spscore', 'sprank', 'expect', 'modifications', 'hit_rank', 'peptide',
    #    'num_tot_proteins', 'num_matched_ions', 'tot_num_ions',
    #    'num_missed_cleavages', 'calc_neutral_pep_mass', 'massdiff',
    #    'num_matched_peptides', 'modified_peptide', 'fval', 'ntt', 'nmc',
    #    'massd', 'isomassd', 'peptideprophet_probability',
    #    'peptideprophet_ntt_prob', 'is_rejected']

    def unique_seq(some_list: list[list[str]]) -> list[str]:
        return list({s for lv in some_list for s in lv})

    def join(some_list: list[str]) -> str:
        return ":".join(sorted(set(some_list)))

    # Lei's simple 'use local' rt correction
    def labelled_rt(rts: pd.Series) -> float:
        lr = df.loc[rts.index].isLabelledRun
        if lr.any():
            return rts[lr].median()
        return rts.median()

    agg = dict(
        calc_neutral_pep_mass="median",
        precursor_neutral_mass="median",
        mz="median",
        observed_mz="median",
        retention_time_sec="median" if use_simple_median else labelled_rt,
        num_missed_cleavages="max",
        peptideprophet_probability="max",
        interprophet_probability="max",
        is_decoy="all",
        agg_count="sum",
        # is_rejected="any",
        proteins=unique_seq,
        protein_descr=unique_seq,
        modifications="first",
        xcorr="max",  # COMET searchEngineScore
        ionscore="max",  # MASCOT searchEngineScore
        run=join,
        isLabelledRun="any",
        searchEngineScore="max",
        fdr="max",
    )

    agg_protxml = dict(
        probability="max",
        group_number="nunique",
        percent_coverage="max",
        confidence="max",
        protein_description=unique_seq,
        proteins=unique_seq,
        ngroups="max",
    )
    agg.update(agg_protxml)  # type: ignore
    # only values that exist
    agg = {k: v for k, v in agg.items() if k in df.columns and k not in keys}
    cols = keys + list(agg)
    g = df[cols].groupby(by=keys, as_index=False)

    ret = g.aggregate(agg)
    # if not GROUP_RT:
    #     ret = ret.drop_duplicates(subset=keys + ["retention_time_sec"], keep="first")
    # ret["prStr"] = ret["proteins"].apply(lambda proteins: ", ".join(sorted(proteins)))
    ret["description"] = ret["protein_descr"].apply(
        lambda protein_descr: ", ".join(sorted(protein_descr)),
    )
    # ret["prGroup"] = ret.groupby("prStr").ngroup()
    # remove.append("prStr")
    ret = ret.drop(columns=remove)
    return ret


def pepxml_raw(
    pepxml: PepXMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> pd.DataFrame:
    # from .broken_api import PepXMLDataFrame
    from .pepxml_reader import pepxml_dataframe

    logger.info("reading: %s", pepxml.original.name)
    df = pepxml_dataframe(
        pepxml.original,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )

    logger.info("done: %s", pepxml.original.name)
    return df


def compute_settings(
    df: pd.DataFrame,
    settings: PeptideSettings,
) -> pd.DataFrame:
    def element_count(peptide: str) -> int:
        return settings.getElementCountFromPeptide(peptide)

    max_iso = mk_maxIso(settings)

    def mzranges(pep: PepXMLRunRow) -> np.ndarray:
        return settings.eic_mzranges(pep)

    logger.info(
        "compute_settings: adding labelledElementCount, maxIso, mzranges",
    )
    df["labelledElementCount"] = df["peptide"].apply(element_count)
    # get rid of peptides with no labelled Elements
    zero = df["labelledElementCount"] == 0
    anyz = zero.sum()
    if anyz > 0:
        logger.warning("removing %s peptides with no labelled element", anyz)
        df = df[~zero].copy()
    df["maxIso"] = df["peptide"].apply(max_iso)
    # ndarray[maxIso+2,2] of mzmin,mzmax
    df["mzranges"] = df[["maxIso", "assumed_charge", "mz", "observed_mz"]].apply(
        mzranges,
        axis=1,
    )
    logger.info("compute_settings: done")
    return df


def getpepxml(
    pepxml: PepXMLResourceFile,
) -> pd.DataFrame:
    if pepxml.cache_pepxml_ok():
        data = pepxml.cache_pepxml()
        logger.info('getpepxml: reading: "%s"', data.name)
        df = IO(data).read_df()
        logger.info('getpepxml: finished reading: "%s" [%d]', data.name, len(df))

    else:
        if not pepxml.exists:
            raise RuntimeError(f"can't find file: {pepxml.original}")
        logger.info('getpepxml: creating cache "%s"', pepxml.original.name)
        pepxml_create(pepxml)
        assert pepxml.cache_pepxml_ok()
        df = IO(pepxml.cache_pepxml()).read_df()
    return df


def filter_pepxml(df: pd.DataFrame, job: TurnoverJob) -> pd.DataFrame:
    from .filters import PepXMLFilter

    if job.match_runNames:
        df = df[df["run"].isin(job.runNames)].copy()
        logger.info('filter_pepxml: run names: "%s" [%d]', job.runNames, len(df))

    filter = PepXMLFilter(minProbabilityCutoff=job.settings.minProbabilityCutoff)
    df = filter.filter(df, copy=True)

    if "agg_count" not in df.columns:
        logger.info("aggregating: %d", len(df))
        df = aggregateSearchHits(
            df,
            settings=job.settings,
            runNames=job.runNames,
        )
        logger.info("aggregating done: %d", len(df))

    df = compute_settings(df, job.settings)
    # df = df.iloc[0:100]  # DEBUG
    return df


def process_pep_prot(job: TurnoverJob) -> pd.DataFrame:
    files = job.to_resource_files()
    ret = []
    for pepxml in files.pepxmls:
        pepxml_df = getpepxml(pepxml)

        pepxml_df = filter_pepxml(pepxml_df, job)
        ret.append(pepxml_df)
    pepxml_df = pd.concat(ret, axis=0, ignore_index=True)

    return pepxml_df


def pepxml_out(
    df: pd.DataFrame,
    pepxml: PepXMLResourceFile,
) -> None:
    from .utils import IO

    data = pepxml.cache_pepxml()

    if logger.isEnabledFor(logging.INFO):
        if "agg_count" in df.columns:
            logger.info(  # pylint: disable=logging-fstring-interpolation
                f"writing file: {data.name}: total={len(df)} multiple={(df.agg_count > 1).sum()}",
            )
        else:
            logger.info("writing file: %s: total=%s", data.name, len(df))

    df = dehydrate_pepxml(df)
    IO(data, df).save_df()

    if logger.isEnabledFor(logging.INFO):
        mem = df.memory_usage(deep=True)
        size = data.stat().st_size
        osize = pepxml.original.stat().st_size
        runs = ",".join(sorted(df.run.unique()))
        logger.info(  # pylint: disable=logging-fstring-interpolation
            f"memory={human(mem.sum())} disk={human(size)} original={human(osize)}: runs={runs}",
        )


def pepxml_create(
    pepxml: PepXMLResourceFile,
    level: int = 0,
    number_of_bg_processes: int = 1,
) -> int:
    df = pepxml_raw(
        pepxml,
        level=level,
        number_of_bg_processes=number_of_bg_processes,
    )
    pepxml_out(df, pepxml)
    return level


def dehydrate_pepxml(df: pd.DataFrame) -> pd.DataFrame:
    if "mzranges" in df.columns:
        df["mzranges"] = df["mzranges"].apply(lambda x: x.flatten())
    return df


def pepok(target: PepXMLResourceFile, force: bool) -> bool:
    if not force and target.cache_pepxml_ok():
        return True
    return False
