"""Browser app"""

import matplotlib.pyplot as plt
import streamlit as st

import triodos_fund_analyzer as tfa
from triodos_fund_analyzer.funds import details_df


def build_page():
    st.title("Triodos Fund Analyzer")
    fig, ax = plt.subplots()
    ax.clear()
    options = dict(
        normalize=st.session_state["normalize"]
        if st.session_state["normalize"] > 0
        else False,
        purchasing_power=(
            st.session_state["purchasing_power"]
            if st.session_state["purchasing_power"] != "off"
            else False
        ),
        deduce_costs=st.session_state["deduce_costs"],
        consider_dividends=st.session_state["consider_dividends"],
        start_date=st.session_state["start_date"],
        add_baseline=st.session_state["add_baseline"],
    )
    for fund in st.session_state["funds"]:
        tfa.plot_history(fund, ax=ax, **options)
    ax.set_xlabel("")
    ax.legend()
    fig.tight_layout()
    plt.ion()
    plt.show()
    st.pyplot(fig=fig, clear_figure=True, use_container_width=True)


if __name__ == "__main__":
    st.sidebar.segmented_control(
        "Funds",
        details_df.index.values,
        selection_mode="multi",
        key="funds",
        help=details_df.full_name.to_string(),
    )
    st.sidebar.slider("normalize", 0, 100, 100, key="normalize")
    st.sidebar.segmented_control(
        "purchasing power",
        ["off", "CPI", "HICP"],
        default="CPI",
        help="Choose index to account for inflation",
        key="purchasing_power",
    )
    st.sidebar.toggle(
        "deduce costs",
        True,
        help="Reduce fund value by fund costs and service fees",
        key="deduce_costs",
    )
    st.sidebar.toggle("consider dividends", True, key="consider_dividends")
    st.sidebar.date_input("start date", "1990-01-01", key="start_date")
    st.sidebar.toggle("add baseline", True, key="add_baseline")

    build_page()
