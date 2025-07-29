from __future__ import annotations

import operator
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import replace
from typing import Any
from typing import Callable
from typing import Literal
from typing import NamedTuple

import numpy as np
import pandas as pd  # type: ignore
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy import join
from sqlalchemy import or_
from sqlalchemy import Select
from sqlalchemy import select
from sqlalchemy import Subquery
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Relationship
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.expression import BinaryExpression
from typing_extensions import override

from .model import PepProt
from .model import Peptide
from .model import Protein
from .utils import rehydrate_peptides
from .utils import round10

# from sqlalchemy.orm import load_only
# from sqlalchemy.orm import selectinload
# from sqlalchemy.orm import Session


# func.count()
# pylint: disable=not-callable
class WhereClauses(NamedTuple):
    pep_where: ColumnElement[bool] | None
    prot_where: ColumnElement[bool] | None


@dataclass
class FormFilter:
    peptideQualityFilter: float | None = None
    heavyMinCor: float | None = None
    isoPeaksNr: float | None = None
    isoPeaksMinRSQ: float | None = None
    #    heavyMinRSQ: float | None = None
    monoMinus1MinRatio: float | None = None
    # enrichmentFactor: float | None = None
    enrichmentMax: float | None = None
    enrichmentMin: float | None = None
    fdrMaximum: float | None = None
    nnlsResidual: float | None = None
    maxPeakArea: float | None = None
    log_sigma_lpf: float | None = None

    def calc_where(self, scale_intensity: bool = False) -> WhereClauses:
        pep_filters = []
        prot_filters = []

        def add(q: Any) -> None:
            pep_filters.append(q)

        if self.peptideQualityFilter is not None:
            add(Peptide.peptideprophet_probability >= self.peptideQualityFilter)

        if self.fdrMaximum is not None:
            add(Peptide.fdr <= self.fdrMaximum)

        if self.heavyMinCor is not None:
            add(Peptide.heavyCor >= self.heavyMinCor)

        # if self.heavyMinRSQ is not None:
        #     add(Peptide.heavy_adj_r_squared >= self.heavyMinRSQ)

        if self.nnlsResidual is not None:
            if scale_intensity:
                add(
                    Peptide.nnls_residual / Peptide.totalIntensityWeight
                    <= self.nnlsResidual,
                )
            else:
                add(
                    Peptide.nnls_residual / Peptide.totalNNLSWeight
                    <= self.nnlsResidual,
                )

            # add(func.power(Peptide.nnls_residual,2) <= self.nnlsResidual)
            # add(Peptide.nnls_residual <= self.nnlsResidual)

        if self.monoMinus1MinRatio is not None:
            add(Peptide.inv_ratio < 1.0 / self.monoMinus1MinRatio)

        if self.enrichmentMax is not None:
            add(Peptide.enrichment <= self.enrichmentMax)
        if self.enrichmentMin is not None:
            add(Peptide.enrichment >= self.enrichmentMin)

        if self.maxPeakArea is not None:
            add(Peptide.maxPeakArea >= self.maxPeakArea)

        if self.log_sigma_lpf is not None:
            prot_filters.append(
                func.log((Protein.lpf_std + 1e-4) / Protein.lpf_median)
                <= self.log_sigma_lpf,
            )

        if (
            self.isoPeaksNr is not None
            and self.isoPeaksMinRSQ is not None
            and self.isoPeaksMinRSQ != -1.0  # not set
        ):
            col = getattr(Peptide, f"iso_peaks_nr_{int(self.isoPeaksMinRSQ)}", None)
            if col is not None:
                add(col >= int(self.isoPeaksNr))

        return WhereClauses(
            and_(*pep_filters) if pep_filters else None,
            and_(*prot_filters) if prot_filters else None,
        )


def like(attr: InstrumentedAttribute, value: str) -> BinaryExpression[bool]:
    if "%" not in value:
        value = "%" + value + "%"
    return attr.like(value)


def doregex(attr: InstrumentedAttribute, value: str) -> BinaryExpression[bool]:
    return attr.op("REGEXP")(value)  # need pcre installed in sqllite


OPMAP: dict[str, Callable[..., Any]] = {
    ">": operator.gt,
    ">=": operator.ge,
    "=": operator.eq,
    "<": operator.lt,
    "<=": operator.le,
    "!=": operator.ne,
    "like": like,
    "regex": doregex,
}


def okcolumn(name: str, Orm: type[DeclarativeBase]) -> bool:
    attr = getattr(Orm, name)
    if attr is None or not hasattr(attr, "property"):
        return False
    if isinstance(attr.property, Relationship):
        return False
    return True


class RowQuery(NamedTuple):
    column: str
    op: str
    value: Any

    def to_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        attr = getattr(Orm, self.column, None)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(f"unknown column {self.column} for {Orm}")
        if isinstance(attr.property, Relationship):
            raise ValueError(f"column {self.column} is a relationship on {Orm}!")
        op = OPMAP.get(self.op)
        if op is None:
            raise ValueError(f"no operator like {self.op}")

        return op(attr, self.value)


@dataclass
class RowFilter:
    rows: list[RowQuery]
    method: Literal["and", "or"] = "or"

    def add(self, more: RowFilter) -> RowFilter:
        return replace(self, rows=self.rows + more.rows)

    def to_and_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        return and_(*[q.to_sql(Orm) for q in self.rows])

    def to_or_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        return or_(*[q.to_sql(Orm) for q in self.rows])

    def to_sql(self, Orm: type[DeclarativeBase]) -> ColumnElement[bool]:
        if self.method == "and":
            return self.to_and_sql(Orm)
        return self.to_or_sql(Orm)


@dataclass
class DTQuery:
    start: int = 0
    length: int = 10
    search: str | None = None
    regex: bool = False
    ascending: bool = True
    order_column: str | None = None
    draw: int = 0  # data tables


def search_protein_tosql(search: str, search_columns: list[str]) -> ColumnElement[bool]:
    return RowFilter(
        [RowQuery(coln, "like", search) for coln in search_columns],
    ).to_or_sql(Protein)


@dataclass
class ProteinQueryResult:
    result_df: pd.DataFrame
    total_proteins: int = -1
    total_peptides: int = -1
    total_filtered: int = -1


def np_agg(val: str | None, func: Callable[[np.ndarray], float]) -> float | None:
    if val is None:
        return None
    values = np.array([float(v) for v in val.split(",")])
    if len(values) == 0:
        return np.nan
    return func(values)


def std(val: str | None) -> float | None:
    return np_agg(val, np.std)


def median(val: str | None) -> float | None:
    return np_agg(val, np.median)


# sqlite is missing some aggregate functions... we "fake" them here.
FAKE_AGGREGATE_FUNCS = {"std": std, "median": median}


# see https://www.sqlite.org/lang_aggfunc.html
@dataclass(kw_only=True)
class Aggregate:
    column: str
    aggfunc: str  # aggregate function sum,avg,group_concat etc.
    label: str = ""
    args: Sequence[str] | str = ()

    def __post_init__(self) -> None:
        if self.label == "":
            self.label = self.column
        if isinstance(self.args, str):
            self.args = [self.args]

    def getattr(
        self,
        orm: type[DeclarativeBase],
        column: str,
    ) -> ColumnElement[Any]:
        attr = getattr(orm, column)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(f"unknown column {column} for {orm}")
        if isinstance(attr.property, Relationship):
            raise ValueError(f"column {column} is a relationship on {orm}!")
        return attr

    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        return self.getattr(orm, self.column)

    def make_column(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        attr = self.getcolumn(orm)

        if self.aggfunc in FAKE_AGGREGATE_FUNCS:
            aggf = getattr(func, "group_concat")
            attr = aggf(attr, ",")
        else:
            aggf = getattr(func, self.aggfunc)
            attr = aggf(attr, *self.args)
        return attr.label(self.label)


@dataclass(kw_only=True)
class RatioAggregate(Aggregate):
    denom: str = "totalNNLSWeight"

    @override
    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any]:
        attr = self.getattr(orm, self.column)
        denom = self.getattr(orm, self.denom)
        return attr / denom


@dataclass
class Column:
    name: str
    title: str = ""  # Title for datatables.net
    read: bool = True  # read this column from data table
    send: bool = True  # send this column to browser
    view: bool = True  # show this column as datatables column
    search: bool = True  # search this column given search query
    aggregate: Aggregate | None = None  # is an aggregate column
    className: str | None = None  # possible className for datatables.net
    denom: str | None = None

    def __post_init__(self) -> None:
        if self.title == "":
            self.title = self.name
        if self.aggregate is not None:
            if not isinstance(self.aggregate, Aggregate):
                if "denom" in self.aggregate:
                    self.aggregate = RatioAggregate(**self.aggregate)
                else:
                    self.aggregate = Aggregate(**self.aggregate)
            if self.aggregate.label != self.name:
                self.aggregate = replace(self.aggregate, label=self.name)
            self.search = False
            self.read = False

    def getcolumn(self, orm: type[DeclarativeBase]) -> ColumnElement[Any] | None:
        ret = getattr(orm, self.name, None)
        if ret is None:
            return None
        if self.denom is not None:
            denom = getattr(orm, self.denom, None)
            if denom is not None:
                return (ret / denom).label(self.name)
        return ret


class ProteinQuery:
    Join = join(PepProt, Peptide)
    # QID = select(PepProt.proteinid).select_from(Join)
    NPRO = select(func.count(PepProt.proteinid.distinct())).select_from(Join)
    COUNT_PROTEIN = select(func.count(Protein.proteinid))
    # NPEP = select(func.count(PepProt.peptideid.distinct())).select_from(Join)
    NPEP = select(func.count(Peptide.peptideid))

    def __init__(
        self,
        peptide_filter: FormFilter | None,
        protein_filter: RowFilter | None = None,
        *,
        dtquery: DTQuery | None = None,
        columns: list[Column] | None = None,
    ):
        self.protein_filter = protein_filter.to_sql(Protein) if protein_filter else None
        if peptide_filter is not None:
            self.peptide_filter, prot_where = peptide_filter.calc_where()
            if prot_where is not None:
                self.protein_filter = (
                    and_(prot_where, self.protein_filter)
                    if self.protein_filter is not None
                    else prot_where
                )

        else:
            self.peptide_filter = None
        if columns is None:
            columns = []
        self.dtquery = dtquery
        self.columns = columns
        self.search_columns = [c.name for c in self.columns if c.search]
        self.aggregates = [c.aggregate for c in self.columns if c.aggregate is not None]
        self.protein_columns = (
            [
                attr
                for col in self.columns
                if col.send and col.read
                for attr in [self.getcolumn(col)]
                if attr is not None
            ]
            if self.columns
            else [Protein]  # type: ignore
        )

        npro = self.NPRO
        # qid = self.QID
        npep = self.NPEP
        if self.peptide_filter is not None:
            npro = npro.where(self.peptide_filter)  # type: ignore
            # qid = qid.where(self.peptide_filter)  # type: ignore
            npep = npep.where(self.peptide_filter)  # type: ignore
        self.npro = npro
        # self.qid = qid
        self.npep = npep

    def make_agg(self, agg: Aggregate) -> ColumnElement[Any]:
        return agg.make_column(Peptide)

    def peptide_subquery(self, aggregates: Sequence[Aggregate]) -> Subquery:
        aggs = [self.make_agg(agg) for agg in aggregates]
        columns = [PepProt.proteinid, *aggs]
        q = select(*columns).select_from(self.Join)
        if self.peptide_filter is not None:
            q = q.where(self.peptide_filter)
        q = q.group_by(PepProt.proteinid)
        return q.subquery()

    def getcolumn(self, col: Column) -> ColumnElement[Any]:
        attr = col.getcolumn(Protein)
        if attr is None or not hasattr(attr, "property"):
            raise ValueError(f"unknown column {col} for protein table")
        if isinstance(attr.property, Relationship):
            raise ValueError(f"column {col} is a relationship on protein!")
        return attr

    def query(
        self,
        engine: Engine,
        want_all: bool = True,
    ) -> ProteinQueryResult:
        qid = self.peptide_subquery(self.aggregates)
        cols = qid.columns[1:]
        columns = self.protein_columns + list(cols)

        q: Select[Any] = select(*columns)
        q = q.join(qid, qid.c.proteinid == Protein.proteinid)
        # if self.peptide_filter is not None:
        #     q = q.where(Protein.proteinid.in_(self.qid))
        if self.protein_filter is not None:
            q = q.where(self.protein_filter)

        q, tq = self.process_query(q)

        tq = tq.join(qid, qid.c.proteinid == Protein.proteinid)
        total_proteins = total_peptides = total_filtered = -1
        with engine.begin() as conn:
            if want_all:
                total_proteins = conn.execute(self.npro).scalar() or 0
                total_peptides = conn.execute(self.npep).scalar() or 0
                total_filtered = conn.execute(tq).scalar() or 0
            df = pd.read_sql_query(q, con=conn)
            # sigh! sqllite does not have a std aggregate function
            # so we group_concat and the parse and the string again...
            for a in self.aggregates:
                if a.aggfunc in FAKE_AGGREGATE_FUNCS:
                    df[a.label] = df[a.label].apply(FAKE_AGGREGATE_FUNCS[a.aggfunc])

        return ProteinQueryResult(
            self.rehydrate(df),
            total_proteins,
            total_peptides,
            total_filtered,
        )

    def process_query(self, query: Select[Any]) -> tuple[Select[Any], Select[Any]]:
        q = self.dtquery
        if q:
            if q.search is not None and self.search_columns is not None:
                query = query.where(search_protein_tosql(q.search, self.search_columns))
            if q.order_column is not None:
                col = getattr(Protein, q.order_column, None)
                if col is not None:
                    query = query.order_by(col.asc() if q.ascending else col.desc())
                else:
                    # virtual
                    if q.order_column in {a.label for a in self.aggregates}:
                        asc = "ASC" if q.ascending else "DESC"
                        query = query.order_by(text(f"{q.order_column} {asc}"))

        filtered_total = self.COUNT_PROTEIN
        if query.whereclause is not None:
            filtered_total = filtered_total.where(query.whereclause)

        if q and q.length > 0:
            query = query.slice(q.start, q.start + q.length)
        return query, filtered_total

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return rehydrate_peptides(df)


class PeptideQuery:
    Join = join(PepProt, Protein)
    QID = select(PepProt.peptideid).select_from(Join)

    def __init__(
        self,
        peptide_filter: FormFilter | None = None,
        protein_filter: RowFilter | None = None,
        *,
        peptide_columns: list[Column] | None = None,
        filtered_column: str | None = None,
    ):
        self.protein_filter = protein_filter.to_sql(Protein) if protein_filter else None

        qid = self.QID
        if self.protein_filter is not None:
            qid = qid.where(self.protein_filter)  # type: ignore

        self.qid = qid
        if peptide_filter is not None:
            clause = peptide_filter.calc_where()
            self.peptide_filter = clause.pep_where
            # if clause.prot_where is not None:
            #     self.qid = self.qid.where(clause.prot_where)
        else:
            self.peptide_filter = None
        self.filtered_column = filtered_column
        self.peptide_columns = peptide_columns

    def getcolumn(self, col: Column) -> ColumnElement[Any] | None:
        return col.getcolumn(Peptide)

    def query(
        self,
        engine: Engine,
    ) -> pd.DataFrame:
        cols = (
            [
                attr
                for col in self.peptide_columns
                if col.read
                for attr in [self.getcolumn(col)]
                if attr is not None
            ]
            if self.peptide_columns
            else [Peptide]  # type: ignore
        )

        if self.peptide_filter is not None and self.filtered_column is not None:
            cols.append(self.peptide_filter.label(self.filtered_column))

        q: Select[Any] = select(*cols)
        if self.protein_filter is not None:
            q = q.where(Peptide.peptideid.in_(self.qid))
        if self.peptide_filter is not None and self.filtered_column is None:
            q = q.where(self.peptide_filter)

        with engine.begin() as conn:
            q = self.process_query(q, conn)
            df = pd.read_sql_query(q, con=conn)
            return self.rehydrate(df)

    def process_query(self, q: Select[Any], conn: Connection) -> Select[Any]:
        return q

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return rehydrate_peptides(df)


class SimplePeptideQuery:
    def __init__(
        self,
        peptide_filter: RowFilter | None = None,
        extra: FormFilter | None = None,
        *,
        peptide_columns: list[Column] | None = None,
    ):
        self.peptide_filter = peptide_filter.to_sql(Peptide) if peptide_filter else None
        self.extra = extra
        self.peptide_columns = peptide_columns

    def getcolumn(self, col: Column) -> ColumnElement[Any] | None:
        return col.getcolumn(Peptide)

    def query(
        self,
        engine: Engine,
    ) -> pd.DataFrame:
        q: Select[Any] = select(
            *(
                [
                    attr
                    for col in self.peptide_columns
                    if col.read
                    for attr in [self.getcolumn(col)]
                    if attr is not None
                ]
                if self.peptide_columns
                else [Peptide]  # type: ignore
            ),
        )

        if self.peptide_filter is not None:
            q = q.where(self.peptide_filter)
        if self.extra is not None:
            wc = self.extra.calc_where()
            if wc.pep_where is not None:
                q = q.where(wc.pep_where)
            # if wc.prot_where is not None:
            #     q = q.where(wc.prot_where)

        with engine.connect() as conn:
            df = pd.read_sql_query(q, con=conn)
            return self.rehydrate(df)

    def rehydrate(self, df: pd.DataFrame) -> pd.DataFrame:
        return rehydrate_peptides(df)


@dataclass
class Stats:
    max_nnls_residual: float = 1.0
    max_maxPeakArea: float = 0.0
    min_enrichment: float = 0.0
    max_enrichment: float = 1.0


ROUND: dict[str, Callable[[Any], Any]] = {"max_nnls_residual": lambda v: round(v, 2)}


def calc_stats(
    engine: Engine | None,
    round: bool = False,
    scale_intensity: bool = False,
) -> Stats:
    if engine is None:
        return Stats()
    if scale_intensity:
        resid = Peptide.nnls_residual / Peptide.totalIntensityWeight
    else:
        resid = Peptide.nnls_residual / Peptide.totalNNLSWeight
    q = select(
        func.max(resid).label("max_nnls_residual"),
        func.max(Peptide.maxPeakArea).label("max_maxPeakArea"),
        func.min(Peptide.enrichment).label("min_enrichment"),
        func.max(Peptide.enrichment).label("max_enrichment"),
    )
    with engine.connect() as conn:
        row = conn.execute(q).mappings().one()
    if round:
        d = {k: ROUND.get(k, round10)(v) for k, v in row.items()}
    else:
        d = dict(row)
    return Stats(**d)


def sqlite_version(engine: Engine) -> int:
    from .model import Version

    q = select(
        func.max(Version.version).label(
            "version",
        ),
    )
    try:
        with engine.connect() as conn:
            row = conn.execute(q).mappings().one_or_none()
            if row is None:
                return -1
            return row["version"]
    except OperationalError:
        return 0
