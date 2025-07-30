"""Tool to visualize Triodos fund histories"""

__version__ = "0.1.dev1"

__all__ = [
    "CPI",
    "data_path",
    "funds",
    "plot_history",
    "cli",
]

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from typing import Literal

from triodos_fund_analyzer.CPI import get_CPI_series
from triodos_fund_analyzer import funds

data_path = Path(__file__).parent / ".cached_data"
if not data_path.exists():
    data_path.mkdir()


def plot_history(
    fund: str,
    *,
    normalize: bool | float = 100.0,
    purchasing_power: bool | Literal["CPI", "HICP"] = "CPI",
    deduce_costs: bool = True,
    consider_dividends: bool = True,
    start_date: str = None,
    add_baseline: bool = False,
    ax: plt.Axes = None,
) -> plt.Axes:
    trading_value_history = funds.get_trading_value_series(fund)
    if start_date is not None:
        trading_value_history = trading_value_history.loc[start_date:]
    if normalize:
        trading_value_history /= trading_value_history.iloc[0] / (
            normalize if not isinstance(normalize, bool) else 100
        )
    if purchasing_power:
        index = get_CPI_series(harmonized=(purchasing_power == "HICP")).reindex(
            trading_value_history.index, method="ffill"
        )
        trading_value_history /= index / index.iloc[-1]
    relative_dividends = (funds.get_dividends(fund) / trading_value_history).fillna(0)
    fund_details = funds.get_details(fund)
    if deduce_costs:
        trading_value_history *= 0.991 if funds.get_acro(fund) == "TETEF" else 0.996
        relative_costs = pd.Series(
            fund_details.loc[["fond_costs", "service_fee", "transaction_fee"]].sum()
            * trading_value_history.index.diff()
            / pd.Timedelta(365.25, "days"),
            trading_value_history.index,
        )
        if consider_dividends:
            shares = 0.996 * (1 + relative_dividends - relative_costs).cumprod()  #
        else:
            shares = 0.996 * (1 - relative_costs).cumprod()
    else:
        if consider_dividends:
            shares = 1 * (1 + relative_dividends).cumprod()
        else:
            shares = 1
    if ax is None:
        _, ax = plt.subplots()
    line = (
        (shares * trading_value_history)
        .plot(ax=ax, label=funds.get_name(fund))
        .get_lines()[-1]
    )
    if add_baseline:
        baseline_properties = dict(
            color=line.get_c(),
            linewidth=line.get_lw() * 0.67,
            linestyle="dashed",
            zorder=line.zorder - 1,
            label="",
        )
        if purchasing_power:
            (trading_value_history.iloc[0] / (index / index.iloc[0])).plot(
                ax=ax, **baseline_properties
            )
        else:
            ax.hlines(
                trading_value_history.iloc[0],
                *trading_value_history.index[[0, -1]],
                **baseline_properties,
            )
    return ax


def cli():
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="show_fund", description="Visualize fund histories")
    parser.add_argument(
        "--normalize",
        nargs=1,
        default=[100],
        type=float,
        help="Set 0 to disable normalization",
        metavar="12.3",
    )
    parser.add_argument(
        "--purchasing-power",
        nargs=1,
        default=["CPI"],
        type=str,
        choices=["CPI", "HICP", "off"],
        help="Choose index to account for inflation",
    )
    parser.add_argument(
        "--ignore-costs",
        action="store_true",
        help="Do not reduce fund value by fund costs and service fees",
    )
    parser.add_argument(
        "--ignore-dividends",
        action="store_true",
        help="Do not add/reinvest dividends to fund value",
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start the history at provided date",
        metavar="yyyy-mm-dd",
    )
    parser.add_argument(
        "--hide-baseline",
        action="store_true",
        help="Do not show reference purchasing power evolution (will be hidden by "
        "default for 4 shown funds or more)",
    )
    parser.add_argument(
        "funds", nargs="+", help="List funds that should be shown", metavar="fund name"
    )
    args = parser.parse_args()

    options = dict(
        normalize=args.normalize[0] if args.normalize[0] > 0 else False,
        purchasing_power=(
            args.purchasing_power[0] if args.purchasing_power[0] != "off" else False
        ),
        deduce_costs=not args.ignore_costs,
        consider_dividends=not args.ignore_dividends,
        start_date=None if "start" not in args else args.start,
        add_baseline=not args.hide_baseline or len(args.funds) > 3,
    )

    _, ax = plt.subplots()
    for fund in args.funds:
        plot_history(fund, ax=ax, **options)
    ax.set_xlabel("")
    plt.legend()
    plt.ion()
    plt.show(block=True)
