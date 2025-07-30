"""Tools for the consumenten prijs index (CPI)"""

__all__ = [
    "get_CPI_series",
]

import cbsodata
from datetime import datetime
import pandas as pd
from typing import Literal

import triodos_fund_analyzer as tfa


def _download_index(index_acro: Literal["CPI", "HICP"] = "CPI") -> None:
    if index_acro not in ["CPI", "HICP"]:
        raise Exception(f"Unexpected index ID {index_acro}.")
    pd.DataFrame(
        cbsodata.get_data(f"8313{1 if index_acro == 'CPI' else 3}ENG")
    ).set_index("ID").to_csv(tfa.data_path / f"{index_acro}.csv")


def _extract_main_series(df: pd.DataFrame) -> pd.Series:
    #  select "all items" (NL: alle bestedingen)
    df = df.loc[df.iloc(1)[0].apply(lambda x: x.startswith("000000"))].iloc(1)[1:]
    df = df.loc[df.iloc(1)[0].apply(lambda x: len(x) > 4)]  # drop yearly values
    df.index = pd.to_datetime(df.iloc(1)[0], format="%Y %B")
    return df.iloc(1)[-1]


def get_CPI_series(harmonized: bool = False) -> pd.Series:
    _abbr = "CPI" if not harmonized else "HICP"
    path = (tfa.data_path / _abbr).with_suffix(".csv")
    if (
        not path.exists()
        or datetime.now().month > datetime.fromtimestamp(path.stat().st_mtime).month
    ):
        _download_index(_abbr)
    return _extract_main_series(pd.read_csv(path, usecols=[1, 2, 3]))
