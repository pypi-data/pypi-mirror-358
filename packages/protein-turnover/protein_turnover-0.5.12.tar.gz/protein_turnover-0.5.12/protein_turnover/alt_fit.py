from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.fft import irfft
from scipy.fft import irfftn
from scipy.fft import next_fast_len
from scipy.fft import rfft
from scipy.fft import rfftn

from .utils import ensure_pos
from .utils import PeptideInfo
from .utils import resize

if TYPE_CHECKING:
    from typing import Callable
    from .utils import PeptideSettings


def memsize(abundances: np.ndarray, natoms: int) -> int:
    return (next_fast_len(natoms + 1, real=True) ** (len(abundances) - 1)) * 8


# see https://pubs.acs.org/doi/pdf/10.1021/ac500108n
def fractions1(abundances: np.ndarray, natoms: int) -> np.ndarray:
    nlen = next_fast_len(natoms + 1, real=True)
    c = np.zeros(nlen, np.float64)
    c[:2] = abundances

    return irfft(rfft(c, overwrite_x=True) ** natoms, nlen, overwrite_x=True)[
        : natoms + 1
    ]


def fractions(abundances: np.ndarray, iabundance: int, natoms: int) -> np.ndarray:
    if len(abundances) == 2:
        return fractions1(abundances, natoms)
    nlen = next_fast_len(natoms + 1, real=True)
    shape = tuple([nlen] * (len(abundances) - 1))
    m = len(shape)
    c = np.zeros(shape, np.float64)

    z: Callable[[], list[int]] = lambda: [0] * m
    # abundance zero is the main stable isotope
    c[tuple(z())] = abundances[0]

    for i, a in enumerate(abundances[1:]):
        idx = z()
        idx[i] = 1
        c[tuple(idx)] = a

    r = irfftn(rfftn(c, overwrite_x=True) ** natoms, c.shape, overwrite_x=True)

    # pull out iabundance axis
    idx = z()
    idx[iabundance - 1] = slice(natoms + 1)  # type: ignore
    return r[tuple(idx)]  # pylint: disable=invalid-sequence-index


def isotopicDistribution(
    pepinfo: PeptideInfo,
    abundance: float | None = None,
) -> np.ndarray:
    """implements paper https://pubs.acs.org/doi/pdf/10.1021/ac500108n"""
    # also https://dx.doi.org/10.1021/ac500108n

    if abundance is None:
        abundances = pepinfo.naturalAtomicAbundances
    else:
        abundances = pepinfo.labelledAtomicAbundances(abundance)

    r = fractions(abundances, pepinfo.iabundance, pepinfo.elementCount)
    return np.fmax(r, 0.0)


def mk_maxIso(settings: PeptideSettings) -> Callable[[str], np.int32]:
    from .config import ABUNDANCE_CUTOFF

    abundances = settings.labelledAtomicAbundancesAtMaxEnrich
    iabundance = settings.iabundance

    def maxIso(peptide: str) -> np.int32:
        n = settings.getElementCountFromPeptide(peptide)
        r = fractions(abundances, iabundance, n)
        mx = np.max(np.where(r > ABUNDANCE_CUTOFF))
        return mx + 1

    return maxIso


def makeEnvelopeArray(
    pepinfo: PeptideInfo,
    maxIso: int,
) -> tuple[np.ndarray, np.ndarray]:
    enrichments = pepinfo.getEnrichments(maxIso)

    isotopeEnvelopeBasis = np.zeros(
        shape=(maxIso + 1, len(enrichments)),
        dtype=np.float64,
    )
    for i, elementEnrichmentLevel in enumerate(enrichments):
        d = isotopicDistribution(pepinfo, elementEnrichmentLevel)
        maxEl = min(len(d), maxIso + 1)
        isotopeEnvelopeBasis[:maxEl, i] = d[:maxEl]
    return enrichments, isotopeEnvelopeBasis


def heavy_dist(
    pepinfo: PeptideInfo,
    isotopeEnvelopes: np.ndarray,
) -> np.ndarray:
    naturalIsotopeEnvelope = natural_dist(pepinfo, isotopeEnvelopes)
    naturalIsotopeEnvelope = resize(naturalIsotopeEnvelope, len(isotopeEnvelopes) - 1)

    return ensure_pos(
        isotopeEnvelopes[1:] - naturalIsotopeEnvelope,
    ).astype(np.float32)


def natural_dist(
    pepinfo: PeptideInfo,
    isotopeEnvelopes: np.ndarray,
) -> np.ndarray:
    isod = isotopicDistribution(pepinfo)
    denom = isod[0]
    denom = denom if denom > 0.0 else 1.0
    return isotopeEnvelopes[1] * isod / denom
