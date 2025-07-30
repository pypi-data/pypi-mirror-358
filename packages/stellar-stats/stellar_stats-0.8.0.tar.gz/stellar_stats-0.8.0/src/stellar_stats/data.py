import os

import pandas as pd
import streamlit as st
import yfinance as yf

from .stats import return_stats


def load_returns(accounts, datadirs):
    return_dfs = []
    for acct in accounts:
        if acct in datadirs:
            if os.path.exists(f"{datadirs[acct]}/returns.csv"):
                return_dfs.append(
                    pd.read_csv(
                        f"{datadirs[acct]}/returns.csv", index_col=0, parse_dates=True
                    )
                )
            elif os.path.exists(f"{datadirs[acct]}/returns.hdf"):
                return_dfs.append(pd.read_hdf(f"{datadirs[acct]}/returns.hdf"))
            elif os.path.exists(f"{datadirs[acct]}/returns.parquet"):
                return_dfs.append(pd.read_parquet(f"{datadirs[acct]}/returns.parquet"))
            else:
                pass
        else:
            pass

    if len(return_dfs) > 1:
        returns = pd.concat(return_dfs).groupby(level=0).sum()
        returns = return_stats(returns)
    elif len(return_dfs) == 1:
        returns = return_dfs[0]
    else:
        returns = None

    return returns


@st.cache_data
def load_remote(symbol):
    data_df = yf.download(symbol, start="2000-01-01", auto_adjust=True)
    data_df.columns = data_df.columns.droplevel("Ticker")
    data_df = data_df.sort_index()
    data_df.index.name = "date"
    returns = pd.DataFrame(
        {
            "last_eod_value": data_df["Close"].shift(1).dropna(),
            "account_value": data_df["Close"][1:],
            "cashflow": 0,
            "returns": data_df["Close"].pct_change().dropna(),
        }
    )
    return returns


def load_benchmark(benchmark, index_funcs, datadirs):
    if benchmark in index_funcs:
        index_df = index_funcs[benchmark]()
        if "trade_date" in index_df.columns:
            index_df["date"] = pd.to_datetime(index_df["trade_date"])
            index_df = index_df.set_index("date")
            index_df = index_df.sort_index()
            bm_returns = pd.DataFrame(
                {
                    "last_eod_value": index_df["close"].shift(1).dropna(),
                    "account_value": index_df["close"][1:],
                    "cashflow": 0,
                    "returns": index_df["close"].pct_change().dropna(),
                }
            )
        else:
            bm_returns = index_df
    elif benchmark in datadirs:
        if os.path.exists(f"{datadirs[benchmark]}/returns.csv"):
            bm_returns = pd.read_csv(
                f"{datadirs[benchmark]}/returns.csv", index_col=0, parse_dates=True
            )
        elif os.path.exists(f"{datadirs[benchmark]}/returns.hdf"):
            bm_returns = pd.read_hdf(f"{datadirs[benchmark]}/returns.hdf")
        elif os.path.exists(f"{datadirs[benchmark]}/returns.parquet"):
            bm_returns = pd.read_parquet(f"{datadirs[benchmark]}/returns.parquet")
        else:
            bm_returns = None
    else:
        bm_returns = load_remote(benchmark)

    return bm_returns


@st.cache_data
def load_trades(accounts, datadirs):
    trade_dfs = []

    for acct in accounts:
        if acct in datadirs:
            if os.path.exists(f"{datadirs[acct]}/trades.csv"):
                trade_dfs.append(
                    pd.read_csv(
                        f"{datadirs[acct]}/trades.csv",
                        index_col=0,
                        parse_dates=True,
                        date_format="%Y-%m-%d %H:%M:%S",
                    )
                )
            elif os.path.exists(f"{datadirs[acct]}/trades.hdf"):
                trade_dfs.append(pd.read_hdf(f"{datadirs[acct]}/trades.hdf"))
            elif os.path.exists(f"{datadirs[acct]}/trades.parquet"):
                trade_dfs.append(pd.read_parquet(f"{datadirs[acct]}/trades.parquet"))
            else:
                pass
        else:
            pass

    if len(trade_dfs) == 0:
        trades = None
    else:
        trades = pd.concat(trade_dfs).sort_index()

    return trades


@st.cache_data
def load_round_trips(accounts, datadirs):
    rt_dfs = []
    for acct in accounts:
        if acct in datadirs:
            if os.path.exists(f"{datadirs[acct]}/round_trips.csv"):
                rt_df = pd.read_csv(
                    f"{datadirs[acct]}/round_trips.csv", index_col=0, parse_dates=True
                )
                rt_df["duration"] = pd.to_timedelta(rt_df.duration)
                rt_dfs.append(rt_df)
            elif os.path.exists(f"{datadirs[acct]}/round_trips.hdf"):
                rt_df = pd.read_hdf(f"{datadirs[acct]}/round_trips.hdf")
                rt_dfs.append(rt_df)
            elif os.path.exists(f"{datadirs[acct]}/round_trips.parquet"):
                rt_df = pd.read_parquet(f"{datadirs[acct]}/round_trips.parquet")
                rt_dfs.append(rt_df)
            else:
                pass
        else:
            pass

    if len(rt_dfs) == 0:
        rts = None
    else:
        rts = pd.concat(rt_dfs).sort_index()

    return rts


@st.cache_data
def load_slippage(accounts, datadirs):
    slippage_dfs = []
    for acct in accounts:
        if acct in datadirs:
            if os.path.exists(f"{datadirs[acct]}/slippage.csv"):
                slippage_dfs.append(
                    pd.read_csv(
                        f"{datadirs[acct]}/slippage.csv", index_col=0, parse_dates=True
                    )
                )
            else:
                pass
        else:
            pass

    if len(slippage_dfs) == 0:
        slippage = None
    else:
        slippage = pd.concat(slippage_dfs).sort_index()

    return slippage


@st.cache_data
def load_investor_returns(investors, returns):
    """
    Must be run with full returns history

    investors: Dataframe with [name,account,date,cashflow] columns sorted by date
    returns: Dataframe with date as index, [last_eod_value,account_value,cashflow,today_pnl,returns,cum_returns,net_asset_values,underwater] as columns
    """
    investor_returns = {}

    if investors is None:
        return investor_returns

    # Calculate total fund shares based on all investors' cashflows
    all_cashflows = (
        investors.groupby("date")["cashflow"].sum().reindex(returns.index, fill_value=0)
    )

    # Initialize fund share tracking
    total_shares = 0
    fund_nav_series = returns["net_asset_values"].copy()

    # Calculate total fund shares for each date
    total_shares_series = []
    for date in returns.index:
        if date in all_cashflows.index and all_cashflows[date] != 0:
            nav = fund_nav_series[date]
            if nav > 0:
                total_shares += all_cashflows[date] / nav
        total_shares_series.append(total_shares)

    for investor in investors["name"].unique():
        idf = investors[investors["name"] == investor]
        investor_start_date = idf["date"].iloc[0]
        idf = idf.set_index("date")
        ireturns = returns[returns.index >= investor_start_date]
        ireturns = ireturns.filter(["returns", "net_asset_values"])

        # Merge investor's cashflows
        investor_cashflows = idf.filter(["cashflow"]).reindex(
            ireturns.index, fill_value=0
        )
        ireturns["cashflow"] = investor_cashflows["cashflow"]

        # Calculate investor's shares based on fund-style calculation
        investor_shares = 0
        shares_series = []
        account_values = []
        prev_nav = 1.0  # Initial NAV for first day calculation

        for date, row in ireturns.iterrows():
            cashflow = row["cashflow"]
            today_nav = row["net_asset_values"]

            # Calculate share changes based on cashflow
            if cashflow > 0:
                # Positive cashflow: add shares based on previous day's NAV
                investor_shares += cashflow / prev_nav
            elif cashflow < 0:
                # Negative cashflow: reduce shares based on today's NAV
                investor_shares += cashflow / today_nav  # cashflow is negative

            shares_series.append(investor_shares)

            # Calculate account value using today's NAV
            account_value = investor_shares * today_nav
            account_values.append(round(account_value, 2))

            # Update prev_nav for next iteration
            prev_nav = today_nav

        # Build the investor returns dataframe
        ireturns.insert(0, "shares", shares_series)
        ireturns.insert(1, "account_value", account_values)
        last_eod_values = ireturns["account_value"].shift(1)
        last_eod_values.iloc[0] = 0
        ireturns.insert(1, "last_eod_value", last_eod_values)

        # Calculate today's P&L
        today_pnl = (
            ireturns["account_value"]
            - ireturns["last_eod_value"]
            - ireturns["cashflow"]
        )
        ireturns.insert(3, "today_pnl", today_pnl.round(2))

        # Calculate adjusted last EOD value for return calculation
        ireturns.insert(3, "adj_last_eod_value", ireturns["last_eod_value"])
        ireturns.loc[ireturns["cashflow"] > 0, "adj_last_eod_value"] = (
            ireturns["last_eod_value"] + ireturns["cashflow"]
        )

        # Calculate returns
        ireturns["returns"] = ireturns["today_pnl"] / ireturns["adj_last_eod_value"]
        ireturns["returns"] = ireturns["returns"].fillna(0)

        # Apply return_stats to get cumulative returns and other metrics
        ireturns = return_stats(ireturns)
        ireturns = ireturns.sort_index(ascending=False)
        investor_returns[investor] = ireturns

    return investor_returns


def calculate_max_principle_series(df):
    initial_capital = df["last_eod_value"].iloc[0]
    accumulated_pnl = 0
    net_cashflow = 0
    current_max_principle = initial_capital
    max_principle_values = []

    for _, row in df.iterrows():
        accumulated_pnl += row["today_pnl"]
        net_cashflow += row["cashflow"]

        if net_cashflow > accumulated_pnl:
            new_max = initial_capital + (net_cashflow - accumulated_pnl)
            current_max_principle = max(current_max_principle, new_max)

        max_principle_values.append(current_max_principle)

    return pd.Series(max_principle_values, index=df.index, name="max_principle")
