import glob
import os
from string import Template

import pandas as pd
import streamlit as st
from tabulate import tabulate

from .stats import adjust_rebate


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def get_latest_modified_time(directory):
    # Get list of all files in directory
    files = glob.glob(directory + "/*")

    # Get the last modified times for all files
    last_modified_times = [os.path.getmtime(file) for file in files]

    # Return the latest modification time
    return max(last_modified_times, default=0)


def show_col_desc(df, cols, dtype="float"):
    result = []
    for col in cols:
        result.append(df[col].describe().to_frame().T)
    desc = pd.concat(result)
    if dtype == "float":
        floatfmt = ("", ",.0f", ".3%", ".3%", ".3%", ".3%", ".3%", ".3%", ".3%")
    else:
        floatfmt = "g"
    st.markdown(tabulate(desc, headers="keys", tablefmt="github", floatfmt=floatfmt))


def refresh_cache(datadirs):
    last_modified = 0
    for acct in datadirs:
        ts = get_latest_modified_time(datadirs[acct])
        if ts > last_modified:
            last_modified = ts

    last_data = st.session_state.get("last_data", 0)
    if last_data < last_modified:
        print("Cache data updated")
        st.cache_data.clear()
        st.session_state.last_data = last_modified


def generate_investors_from_cashflow(
    returns,
    investor_name,
    account_name,
    rebate_threshold=0.01,
):
    """
    Generate investors.csv from returns data cashflow, excluding cash rebates.

    Parameters:
    - returns: DataFrame with returns data containing cashflow column
    - investor_name: String name to use for all investor entries
    - account_name: String account name
    - rebate_threshold: Threshold below which cashflows are considered rebates (default 0.01)

    Returns:
    - DataFrame with investor data
    """
    if returns is None or "cashflow" not in returns.columns:
        raise ValueError("Returns data must contain a 'cashflow' column")

    # Apply adjust_rebate to filter out cash rebates like in app.py
    adjusted_returns = adjust_rebate(returns, rebate_threshold)

    # Get significant cashflows (non-zero after rebate adjustment)
    significant_cashflows = adjusted_returns[
        adjusted_returns["cashflow"] != adjusted_returns["cash_rebate"]
    ].copy()

    if len(significant_cashflows) == 0:
        print("No significant cashflows found after filtering rebates")
        return pd.DataFrame(columns=["name", "account", "date", "cashflow"])

    # Create investor data
    investor_data = []
    for date, row in significant_cashflows.iterrows():
        investor_data.append(
            {
                "name": investor_name,
                "account": account_name,
                "date": date.strftime("%Y-%m-%d"),
                "cashflow": row["cashflow"],
            }
        )

    investors_df = pd.DataFrame(investor_data)

    return investors_df
