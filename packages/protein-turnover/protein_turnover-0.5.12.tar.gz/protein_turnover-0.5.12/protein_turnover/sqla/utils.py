from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import Column
from sqlalchemy import func
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy.engine import Engine


def dataframe_sql(df: pd.DataFrame) -> str:
    res = []
    for cname, dtype in df.dtypes.to_dict().items():
        k = dtype.kind
        if k == "f":
            a = "Float"
        elif k == "i":
            a = "Integer"
        elif k == "b":
            a = "Boolean"
        else:
            typ = type(df[cname].iloc[0])
            if typ == str:
                m = df[cname].apply(len).max()
                if m > 4096:
                    a = "Text"
                else:
                    a = f"String({m})"
            else:
                a = "JSON"
        r = f"    {cname} = Column({a})"
        res.append(r)
    return "\n".join(res)


def check_missing_columns(df: pd.DataFrame, Orm: type) -> set[str]:
    i: Table = inspect(Orm)
    dtypes = {c.name for c in i.columns}
    pepcols = {str(s) for s in df.columns}
    return dtypes - pepcols


def dehydrate_floatarray(arr: np.ndarray) -> list[float]:
    return [float(f) for f in arr]


def dehydrate_intarray(arr: np.ndarray) -> list[int]:
    return [int(f) for f in arr]


def rehydrate_pep(df: pd.DataFrame) -> pd.DataFrame:
    df["modifications"] = df.modifications.apply(
        lambda strarr: np.array(strarr, dtype=object),
    )
    return df


def dehydrate_peptide_col(
    peptide_list: list[dict[str, Any]],
) -> list[dict[str, Any] | list[Any]]:
    def fix(v: dict[str, Any]) -> dict[str, Any] | list[Any]:
        if isinstance(v, np.ndarray):
            return dehydrate_peptide_col(v)
        if isinstance(v, dict):
            return {k: fix(vv) for k, vv in v.items()}
        return v

    return [fix(value) for value in peptide_list]


def dehydrate_prot(df: pd.DataFrame) -> pd.DataFrame:
    df["peptide"] = df.peptide.apply(dehydrate_peptide_col)
    df["indistinguishable_protein"] = df.indistinguishable_protein.apply(list)
    df["unique_stripped_peptides"] = df.unique_stripped_peptides.apply(list)
    return df


def secondary(
    pep: pd.DataFrame,
    prot: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    exploded = prot[["proteinid", "protein_name", "unique_stripped_peptides"]].explode(
        "unique_stripped_peptides",
    )
    dfm = pep[["peptideid", "peptide"]].merge(
        exploded,
        how="inner",
        left_on="peptide",
        right_on="unique_stripped_peptides",
    )
    sec = dfm[["peptideid", "proteinid"]]
    names = (
        dfm[["peptideid", "protein_name"]]
        .groupby("peptideid")
        .agg({"protein_name": lambda s: sorted(set(s))})
    )
    names = names.reset_index().rename(columns=dict(protein_name="protein_names"))
    return sec, names


def dehydrate_peptides(df: pd.DataFrame) -> pd.DataFrame:
    if "result_index" in df.columns:
        df.rename(columns=dict(result_index="peptideid"), inplace=True)
    for col in ["proteins", "protein_descr", "modifications"]:
        if col in df.columns:
            df[col] = df[col].apply(list)
    for col in [
        "mzranges",
        "eics",
        # "isotopeRegressions",
        "adjustedRsq",
        "isotopeEnvelopes",
        "monoFitParams",
        "heavyDistribution",
        "labelledEnvelopes",
        "heavyFitParams",
        "theoreticalDist",
    ]:
        if col in df.columns:
            df[col] = df[col].apply(dehydrate_floatarray)
    for col in ["eics_shape"]:
        if col in df.columns:
            df[col] = df[col].apply(dehydrate_intarray)
    return df


def rehydrate_peptides(turn: pd.DataFrame) -> pd.DataFrame:
    from ..utils import Apply

    if "eics" in turn.columns and "eics_shape" in turn.columns:
        turn["eics"] = turn[["eics", "eics_shape"]].apply(
            Apply.eics_reshape_np,
            axis=1,
        )
        turn.drop(columns=["eics_shape"], inplace=True)
    if "mzranges" in turn.columns:
        turn["mzranges"] = turn["mzranges"].apply(
            lambda mz: np.array(mz).reshape((-1, 2)),
        )
    if "isotopeRegressions" in turn.columns:
        turn["isotopeRegressions"] = turn["isotopeRegressions"].apply(
            lambda iso: np.array(iso).reshape((-1, 2)),
        )
    return turn


def show_table_create(name: str, engine: Engine) -> str:
    with engine.connect() as conn:
        return str(
            conn.execute(
                text(f"SELECT sql FROM sqlite_schema WHERE name = '{name}'"),
            ).scalar(),
        )


def round10(x: float | int) -> float | int:
    if x == 0 or not math.isfinite(x):
        return x
    digits = math.ceil(math.log10(abs(x)))
    sign = 1 if x > 0 else -1
    return sign * 10**digits


def std(engine: Engine, col: Column) -> float:
    q = select(
        func.avg(col * col),
        func.avg(col),
        func.count(col),  # pylint: disable=not-callable
    )
    # q = q.select_from(col.table)
    with engine.connect() as conn:
        xx, x, c = conn.execute(q).one()
        r = c / (c - 1) if c > 1 else 1
        v = (xx - x * x) * r
        return math.sqrt(v)
