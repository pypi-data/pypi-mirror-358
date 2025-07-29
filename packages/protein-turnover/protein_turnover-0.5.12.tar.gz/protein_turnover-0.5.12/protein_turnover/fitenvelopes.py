from __future__ import annotations

import warnings
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from math import fabs
from typing import NamedTuple
from typing import TYPE_CHECKING
from typing import TypeVar

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.linalg import LinAlgError
from scipy.linalg import lstsq
from scipy.optimize import curve_fit
from scipy.optimize import nnls
from scipy.special import erf  # pylint: disable=no-name-in-module
from scipy.stats import pearsonr

from .alt_fit import heavy_dist
from .alt_fit import makeEnvelopeArray
from .logger import logger
from .utils import ensure_pos
from .utils import PeptideInfo
from .utils import resize

if TYPE_CHECKING:
    from typing import Callable
    from typing import Iterator
    from .utils import PeptideSettings
    from .types.pepxmltypes import PepXMLRunRowRT

FAIL_E_CURVE = 0
FAIL_W_CURVE = 1
FAIL_W_QUAD = 2
FAIL_W_H_CURVE = 3
FAIL_E_H_CURVE = 4
FAIL_W_PEARSON = 5
FAIL_E_BOUNDARY = 6
FAIL_E_EICS = 7
FAIL_W_PEARSON2 = 8

FAILS = {
    FAIL_E_CURVE: "envelope curve_fit error",
    FAIL_W_CURVE: "envelope curve_fit warning",
    FAIL_W_QUAD: "envelope quadrature warning",
    FAIL_W_H_CURVE: "heavy curve_fit warning",
    FAIL_E_H_CURVE: "heavy curve_fit error",
    FAIL_W_PEARSON: "pearson correlation warning",
    FAIL_E_BOUNDARY: "no intensities withing boundary",
    FAIL_E_EICS: "can't fit EICS",
    FAIL_W_PEARSON2: "pearson correlation warning",
}

LOG_ERRORS = False

R2: float = np.sqrt(2.0).astype(np.float64)
RPI2: float = np.sqrt(np.pi / 2.0).astype(np.float64)
NSIGMA = 2.0
DELTA_ERF: float = (RPI2 * (erf(NSIGMA / R2) - erf(-NSIGMA / R2))).astype(np.float64)
USE_QUAD = False
QUAD_LIMIT = 500


def fails(ival: int) -> str:
    return ", ".join(s for i, s in FAILS.items() if ival & (1 << i))


@dataclass
class IsotopeEnvelope:
    # isotopeRegressions: np.ndarray  # 2-D (x,2)
    adjustedRsq: np.ndarray
    isotopeEnvelopes: np.ndarray  # 1-D
    monoFitParams: np.ndarray  # 1-D  [mu, sigma, scale, baseline]
    inv_ratio: float
    monoPeakArea: float
    maxPeakArea: float


@dataclass
class LabelledEnvelope:
    labelledEnvelopes: np.ndarray  # 1-D
    theoreticalDist: np.ndarray
    relativeIsotopeAbundance: float
    enrichment: float
    # labelEnrichment2: float
    heavyCor: float
    heavyCor2: float
    nnls_residual: float
    totalNNLSWeight: float
    totalIntensityWeight: float


@dataclass
class Envelope(IsotopeEnvelope, LabelledEnvelope):
    fail: int = 0

    @classmethod
    def make_all(
        cls,
        fail: int,
        env: IsotopeEnvelope,
        # heavy: HeavyEnvelope,
        labelled: LabelledEnvelope,
    ) -> Envelope:
        args = {**asdict(env), **asdict(labelled), "fail": fail}
        return cls(**args)  # type: ignore


def normalIntensityFunction(
    rt: float | np.ndarray,
    mu: float,
    sigma: float,
    k: float,
    baseline: float,
) -> float | np.ndarray:
    return k * np.exp(-0.5 * (rt - mu) ** 2 / sigma**2) + baseline


class RSquared(NamedTuple):
    r_squared: float
    adj_r_squared: float


def lm_adjust(
    mat: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    df: int,
) -> RSquared:
    dx = mat @ x - y
    return adjust(dx, y, df)


def curve_adjust(
    func: Callable[[float | np.ndarray, float, float, float], float | np.ndarray],
    popt: np.ndarray,
    x: np.ndarray,
    y: np.ndarray,
    df: int,
) -> RSquared:
    dx = func(x, *popt) - y
    return adjust(dx, y, df)


# https://en.wikipedia.org/wiki/Coefficient_of_determination
def adjust(dx: np.ndarray, y: np.ndarray, df: int) -> RSquared:
    rss = np.sum(dx**2)
    ymean = np.mean(y)
    tss = np.sum((y - ymean) ** 2)
    if tss > 0.0:
        r_squared = 1.0 - rss / tss
        n = len(y)
        if n > df:
            adj_r_squared = 1.0 - ((n - 1) / (n - df)) * (1.0 - r_squared)
        else:
            adj_r_squared = r_squared
    else:
        r_squared, adj_r_squared = np.nan, np.nan
    return RSquared(r_squared, adj_r_squared)


Result = TypeVar("Result")


def catch_warnings(
    func: Callable[[], Result],
    peptide: str,
    msg: str,
    *,
    quiet: bool = not LOG_ERRORS,
) -> tuple[Result, int]:  # Literal[0,1]
    with warnings.catch_warnings(record=True) as warn:
        warnings.simplefilter("always")
        ret = func()
    if warn and not quiet:
        for w in warn:
            message = str(w.message)
            if "\n" in message:
                message, _ = message.split("\n", 1)

            logger.warning(msg, peptide, message)
    return ret, 1 if warn else 0


def fitEIC(
    rawEIC: np.ndarray,  # float[N,2]
    eicIds: np.ndarray,  # bool[N]
    mono_intensity: np.ndarray,  # float[N,2 or 1]
) -> Iterator[list[float]]:
    eic: np.ndarray
    with_origin = mono_intensity.shape[1] == 2
    for eic in rawEIC:
        try:
            intensity = eic[eicIds, 1]
            _res = lstsq(mono_intensity, intensity)
            assert _res is not None
            x, _residues, rank, _s = _res
            if with_origin:
                alpha, slope = x
            else:
                alpha, slope = 0.0, x[0]

            r = lm_adjust(mono_intensity, x, intensity, df=rank)
            adj_r_squared = r.adj_r_squared
        except LinAlgError as e:
            if LOG_ERRORS:
                logger.error("fitEIC: %s", e)
            adj_r_squared, slope, alpha = np.nan, np.nan, np.nan
        yield [adj_r_squared, slope, alpha]


def fitMonoEnvelope(peptide: str, monoEIC: np.ndarray) -> tuple[float, float] | None:
    from .config import INTERPOLATE_INTENSITY  # pylint: disable=import-outside-toplevel

    monoData: pd.DataFrame
    rt, intensity = monoEIC[:, 0], monoEIC[:, 1]
    if INTERPOLATE_INTENSITY:

        interpolated_rt = np.arange(rt.min(), rt.max() + 1e-4, step=0.5)

        # for fill_value='extrapolate'
        # see https://stackoverflow.com/questions/45429831/valueerror-a-value-in-x-new-is-above-the-interpolation-range-what-other-re
        # interpolated = interp1d(
        #     rt,
        #     intensity,
        #     assume_sorted=True,
        #     axis=0,
        #     fill_value="extrapolate",
        # )
        # interpolated_i = interpolated(interpolated_rt)

        interpolated_i = np.interp(interpolated_rt, rt, intensity)
        monoData = pd.DataFrame(dict(rt=interpolated_rt, int=interpolated_i))
        monoData["int"] = monoData["int"].rolling(5, min_periods=1, center=True).mean()
    else:
        monoData = pd.DataFrame(dict(rt=rt, int=intensity))

    monoData = monoData.dropna(axis="index")

    i = monoData["int"].argmax()
    pos = monoData.iloc[i]

    # returns a smaller sigma than R
    def fit() -> np.ndarray:
        popt, *_ = curve_fit(
            normalIntensityFunction,
            monoData["rt"].to_numpy(),
            monoData["int"].to_numpy(),
            p0=(pos["rt"], 3.0, pos["int"], 50.0),
            # method="lm"
            # maxfev=100,
        )
        return popt

    try:
        popt, fail = catch_warnings(
            fit,
            peptide,
            "fitIsotopeEnvelopes::curve_fit[%s]: %s",
        )
        fail = fail << FAIL_W_CURVE

    except (RuntimeError, TypeError) as e:
        if LOG_ERRORS:
            logger.error("fitIsotopeEnvelopes::curve_fit[%s]: %s", peptide, e)
        return None
    popt[1] = fabs(popt[1])  # ensure sigma is positive

    mu, sigma, _kscale, _base = popt
    ret = rt.min(), rt.max()

    rng = ret[1] - ret[0]
    if ret[0] <= mu <= ret[1] and sigma <= 2 * rng:
        return mu + rng / 2, mu + rng / 2
    return None


@dataclass
class EFit:
    area: float
    lBoundary: float
    rBoundary: float
    fail: int = 0
    popt: np.ndarray = field(default_factory=lambda: np.zeros(4))


def fitIsotopeEnvelope(
    peptide: str,
    rt: np.ndarray,
    intensity: np.ndarray,
) -> EFit:
    from .config import INTERPOLATE_INTENSITY

    if INTERPOLATE_INTENSITY:
        interpolated_rt = np.arange(rt.min(), rt.max() + 1e-4, step=0.5)
        # for fill_value='extrapolate'
        # see https://stackoverflow.com/questions/45429831/valueerror-a-value-in-x-new-is-above-the-interpolation-range-what-other-re
        # interpolated = interp1d(
        #     rt,
        #     intensity,
        #     assume_sorted=True,
        #     axis=0,
        #     fill_value="extrapolate",
        # )
        # interpolated_i = interpolated(interpolated_rt)
        interpolated = lambda rtv: np.interp(rtv, rt, intensity)
        interpolated_i = interpolated(interpolated_rt)
        monoData = pd.DataFrame(dict(rt=interpolated_rt, int=interpolated_i))
        monoData["int"] = monoData["int"].rolling(5, min_periods=1, center=True).mean()
    else:
        monoData = pd.DataFrame(dict(rt=rt, int=intensity))

    monoData = monoData.dropna(axis="index")

    i = monoData["int"].argmax()  # pylint: disable=unsubscriptable-object
    pos = monoData.iloc[i]

    # returns a smaller sigma than R
    def fit() -> np.ndarray:
        popt, *_ = curve_fit(
            normalIntensityFunction,
            monoData["rt"].to_numpy(),
            monoData["int"].to_numpy(),
            p0=(pos["rt"], 3.0, pos["int"], 50.0),
            # method="lm"
            # maxfev=100,
        )
        return popt

    try:
        popt, fail = catch_warnings(
            fit,
            peptide,
            "fitIsotopeEnvelopes::curve_fit[%s]: %s",
        )
        fail = fail << FAIL_W_CURVE

    except (RuntimeError, TypeError) as e:
        if LOG_ERRORS:
            logger.error("fitIsotopeEnvelopes::curve_fit[%s]: %s", peptide, e)
        return EFit(0.0, 0.0, 0.0, 1 << FAIL_E_CURVE)
    popt[1] = fabs(popt[1])  # ensure sigma is positive

    mu, sigma, kscale, base = popt

    lBoundary: float = max(mu - NSIGMA * sigma, rt[0])
    rBoundary: float = min(mu + NSIGMA * sigma, rt[-1])

    eicIds = (rt >= lBoundary) & (rt <= rBoundary)

    if eicIds.sum() == 0:
        return EFit(0.0, lBoundary, rBoundary, fail | 1 << FAIL_E_BOUNDARY, popt)

    if USE_QUAD and INTERPOLATE_INTENSITY:

        def integrate() -> float:
            monoPeakArea, _ = quad(
                interpolated,
                lBoundary,
                rBoundary,
                limit=QUAD_LIMIT,
                # epsabs=1e-6,
                epsrel=1e-6,
            )
            return monoPeakArea

        monoPeakArea, fail2 = catch_warnings(
            integrate,
            peptide,
            "fitIsotopeEnvelopes::quad[%s]: %s",
        )
        fail |= fail2 << FAIL_W_QUAD

    else:
        monoPeakArea = base * (rBoundary - lBoundary) + kscale * sigma * RPI2 * (
            erf((rBoundary - mu) / sigma / R2) - erf((lBoundary - mu) / sigma / R2)
        )
    return EFit(monoPeakArea, lBoundary, rBoundary, fail, popt)


def fitIsotopeEnvelopes(
    peptide: str,
    rawEIC: np.ndarray,
) -> tuple[IsotopeEnvelope | None, int]:
    from .config import WITH_ORIGIN

    monoEIC: np.ndarray = rawEIC[1]
    rt, intensity = monoEIC[:, 0], monoEIC[:, 1]

    efit = fitIsotopeEnvelope(peptide, rt, intensity)
    if efit.fail:
        return None, efit.fail
    eicIds = (rt >= efit.lBoundary) & (rt <= efit.rBoundary)
    intensity = intensity[eicIds]
    if WITH_ORIGIN:
        im = np.c_[np.ones(len(intensity), dtype=np.float32), intensity]
    else:
        im = intensity.reshape(-1, 1)

    isotopeRegressions = np.array(
        list(fitEIC(rawEIC, eicIds, im)),
        dtype=np.float32,
    )  # float[N=maxIso+2,3] # columns: adj_rsquared, alpha, slope (beta)
    alpha, slopes = isotopeRegressions[:, 2], isotopeRegressions[:, 1]
    anynan = np.isnan(slopes)
    nfailed = np.sum(anynan)
    if nfailed == len(slopes):
        return None, 1 << FAIL_E_EICS

    a = alpha * (efit.rBoundary - efit.lBoundary)
    isotopeEnvelopes = ensure_pos(a + efit.area * slopes)

    maxPeakArea = isotopeEnvelopes[1:].max()
    mono = isotopeEnvelopes[1]
    inv_ratio = isotopeEnvelopes[0] / mono if mono > 0.0 else np.inf
    return (
        IsotopeEnvelope(
            adjustedRsq=isotopeRegressions[:, 0].astype(np.float32),
            isotopeEnvelopes=isotopeEnvelopes.astype(np.float32),
            # mu, sigma, scale, baseline
            monoFitParams=efit.popt.astype(
                np.float32,
            ),  # for plotting the fitted gaussian
            inv_ratio=inv_ratio,
            monoPeakArea=efit.area,
            maxPeakArea=maxPeakArea,
        ),
        efit.fail,
    )


EPS = 1e-10


def labelledEnvelopeCalculation(
    peptide: str,
    maxIso: int,
    isotopeEnvelopeInfo: IsotopeEnvelope,
    settings: PeptideSettings,
) -> tuple[LabelledEnvelope, int]:
    pepinfo = PeptideInfo(peptide, settings)
    enrichments, isotopeEnvelopeBasis = makeEnvelopeArray(
        pepinfo,
        maxIso,
    )

    isotopeEnvelopes = isotopeEnvelopeInfo.isotopeEnvelopes
    isotopeEnvelopes = resize(ensure_pos(isotopeEnvelopes[1:]), maxIso + 1)

    labelledEnvelopes, nnls_residual = nnls(isotopeEnvelopeBasis, isotopeEnvelopes)

    totalNNLSWeight = labelledEnvelopes.sum() + EPS
    totalIntensityWeight = isotopeEnvelopes.sum() + EPS

    # labelEnrichment = 0.0
    labelEnrichment2 = 0.0
    relativeIsotopeAbundance = 0.0

    if totalNNLSWeight > 0:
        # this is the same as LPF (other authors had different definitions of RIA)
        relativeIsotopeAbundance = 1.0 - labelledEnvelopes[0] / totalNNLSWeight

        labelEnrichment2 = enrichments @ labelledEnvelopes / totalNNLSWeight
        labelEnrichment2 = min(
            max(0, labelEnrichment2),
            settings.maximumLabelEnrichment,
        )

        # this is mystifing
        # theoreticalMaxEnrichment = elementCount * totalNNLSWeight
        # labelEnrichment = (
        #     (np.array(range(len(labelledEnvelope))) * labelledEnvelope).sum()
        #     / theoreticalMaxEnrichment
        #     * settings.maximumLabelEnrichment
        # )

    theoreticalDist = isotopeEnvelopeBasis @ labelledEnvelopes

    heavyDistribution = heavy_dist(
        pepinfo,
        isotopeEnvelopeInfo.isotopeEnvelopes,
    )
    # heavyDistribution = heavyEnvelopeInfo.heavyDistribution
    nmax = max(len(theoreticalDist), len(heavyDistribution), len(isotopeEnvelopes))
    theoreticalDist = resize(theoreticalDist, nmax)
    heavyDistribution = resize(heavyDistribution, nmax)
    isotopeEnvelopes = resize(isotopeEnvelopes, nmax)

    def fit() -> float:
        res = pearsonr(heavyDistribution, theoreticalDist)
        return res.statistic

    def fit2() -> float:
        res = pearsonr(isotopeEnvelopes, theoreticalDist)
        return res.statistic

    heavyCor, fail = catch_warnings(
        fit,
        peptide,
        "labelledEnvelopeCalculation::pearsonr[%s]: %s",
    )
    fail = fail << FAIL_W_PEARSON
    heavyCor2, fail2 = catch_warnings(
        fit2,
        peptide,
        "labelledEnvelopeCalculation::pearsonr2[%s]: %s",
    )
    fail |= fail2 << FAIL_W_PEARSON2

    return (
        LabelledEnvelope(
            labelledEnvelopes=labelledEnvelopes.astype(np.float32),
            theoreticalDist=theoreticalDist.astype(np.float32),
            relativeIsotopeAbundance=relativeIsotopeAbundance,
            enrichment=labelEnrichment2,
            # labelEnrichment2=labelEnrichment2,
            heavyCor=heavyCor,
            heavyCor2=heavyCor2,
            nnls_residual=nnls_residual,
            totalNNLSWeight=totalNNLSWeight,
            totalIntensityWeight=totalIntensityWeight,
        ),
        fail,
    )


def fitEnvelope(
    pep: PepXMLRunRowRT,  # only need "peptide" , "maxIso"
    rawEIC: np.ndarray,  # [N==pep.maxIso+2,M,2]
    settings: PeptideSettings,
) -> Envelope | None:
    """Fit envelopes to raw EIC matrix of [mzranges, rt, intensity]"""
    iso, faile = fitIsotopeEnvelopes(pep.peptide, rawEIC)
    if iso is None:
        return None
    # heavy, failh = fitHeavyEnvelope(pep.peptide, iso)
    labelled, faill = labelledEnvelopeCalculation(
        pep.peptide,
        pep.maxIso,
        iso,
        # heavy,
        settings,
    )
    return Envelope.make_all(faile | faill, iso, labelled)
