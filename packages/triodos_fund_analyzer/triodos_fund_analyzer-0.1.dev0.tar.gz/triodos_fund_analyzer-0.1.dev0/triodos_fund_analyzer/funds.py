"""Triodos fund module"""

__all__ = [
    "details_df",
]

import pandas as pd
from pathlib import Path
import requests

import triodos_fund_analyzer as tfa

details_df = pd.DataFrame.from_dict(
    {
        "TGF": {
            "unique_id": "NL0000440204",
            "full_name": "Triodos Groenfonds",
            "fond_costs": 0.0097,
            "service_fee": 0.0048,
            "transaction_fee": 0.0,
        },
        "TFSF": {
            "unique_id": "NL0013087968",
            "full_name": "Triodos Fair Share Fund",
            "fond_costs": 0.024,
            "service_fee": 0.0048,
            "transaction_fee": 0.0,
        },
        "TETEF": {
            "unique_id": "NL0013908700",
            "full_name": "Triodos Energy Transition Europe Fund",
            "fond_costs": 0.0258,
            "service_fee": 0.0048,
            "transaction_fee": 0.0005,
        },
        "TMIF": {
            "unique_id": "NL00150022X1",
            "full_name": "Triodos Multi Impact Fund",
            "fond_costs": 0.02,
            "service_fee": 0.0048,
            "transaction_fee": 0.0,
        },
        "TEBIF": {
            "unique_id": "LU0785617936",
            "full_name": "Triodos Euro Bond Impact Fund",
            "fond_costs": 0.0065,
            "service_fee": 0.0048,
            "transaction_fee": 0.0,
        },
        "TIMFD": {
            "unique_id": "LU1956011438",
            "full_name": "Triodos Impact Mixed Fund - Defensive",
            "fond_costs": 0.0085,
            "service_fee": 0.0048,
            "transaction_fee": 0.0001,
        },
        "TIMFN": {
            "unique_id": "LU0785618405",
            "full_name": "Triodos Impact Mixed Fund - Neutral",
            "fond_costs": 0.009,
            "service_fee": 0.0048,
            "transaction_fee": 0.0002,
        },
        "TIMFO": {
            "unique_id": "LU1956012089",
            "full_name": "Triodos Impact Mixed Fund - Offensive",
            "fond_costs": 0.0095,
            "service_fee": 0.0048,
            "transaction_fee": 0.0002,
        },
        "TPIF": {
            "unique_id": "LU0785618744",
            "full_name": "Triodos Pioneer Impact Fund",
            "fond_costs": 0.011,
            "service_fee": 0.0048,
            "transaction_fee": 0.0004,
        },
        "TFGF": {
            "unique_id": "LU2434354713",
            "full_name": "Triodos Future Generations Fund",
            "fond_costs": 0.011,
            "service_fee": 0.0048,
            "transaction_fee": 0.0003,
        },
        "TGEIF": {
            "unique_id": "LU0785617423",
            "full_name": "Triodos Global Equities Impact Fund",
            "fond_costs": 0.01,
            "service_fee": 0.0048,
            "transaction_fee": 0.0003,
        },
    },
    orient="index",
)


def _download_history(fund: str) -> None:
    details = get_details(fund)
    resp = requests.get(
        "https://www.triodos.nl/fund-data-download"
        f"?fund={details.name}"
        f"&isin={details.unique_id}"
        "&price=TRADING_SHARE_PRICE",
        params={"format": "xlsx"},
    )
    if not resp.ok:
        Exception(
            "Error occurred while downloading the data. If this persists, please file "
            f"an issue.\nFailing request URL:\n{resp}"
        )
    with open(get_data_path(fund), "wb") as f:
        f.write(resp.content)


def get_details(fund: str) -> pd.Series:
    if fund in details_df.index:
        return details_df.loc[fund]
    elif fund in details_df.unique_id.values:
        return details_df[details_df.unique_id == fund].iloc[0]
    elif fund in details_df.full_name.values:
        return details_df[details_df.full_name == fund].iloc[0]
    else:
        raise Exception(f"Not a valid fund descriptor: {fund}")


def get_acro(fund: str) -> str:
    return get_details(fund).name


def get_id(fund: str) -> str:
    return get_details(fund).unique_id


def get_name(fund: str) -> str:
    return get_details(fund).full_name


def get_data_path(fund: str) -> Path:
    details = get_details(fund)
    return (tfa.data_path / "-".join([details.name, details.unique_id])).with_suffix(
        ".xlsx"
    )


def get_dividends(fund: str) -> pd.Series:
    if "Dividend History" not in pd.ExcelFile(get_data_path(fund)).sheet_names:
        return 0 * get_trading_value_series(fund).iloc[[-1]]
    return (
        pd.read_excel(
            get_data_path(fund),
            "Dividend History",
            header=7,
            usecols=[2, 3],
            index_col=0,
        )
        .iloc(1)[0]
        .sort_index()
    )


def get_trading_value_series(fund: str) -> pd.Series:
    path = get_data_path(fund)
    if not path.exists():
        _download_history(fund)
    return (
        pd.read_excel(
            path,
            "Historical NAV",
            header=10,
            usecols=[1, 2],
            index_col=0,
        )
        .iloc(1)[0]
        .sort_index()
    )
