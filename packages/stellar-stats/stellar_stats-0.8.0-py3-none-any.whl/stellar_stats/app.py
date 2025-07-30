import datetime
import os

import empyrical as ep
import numpy as np
import pandas as pd
import streamlit as st
from tabulate import tabulate

from .auth import setup_authentication
from .config import load_config, sort_accounts_by_mtime
from .data import (
    calculate_max_principle_series,
    load_benchmark,
    load_investor_returns,
    load_returns,
    load_round_trips,
    load_slippage,
    load_trades,
)
from .stats import (
    adjust_rebate,
    gen_drawdown_table,
    gen_perf,
)
from .ui import (
    plot_cumulative_returns,
    plot_monthly_returns,
    plot_monthly_returns_heatmap,
    plot_profit_distribution,
    plot_return_distribution,
    plot_slippage_distribution,
    plot_underwater,
    plot_weekly_returns,
    plot_yearly_returns,
    show_performance_metrics,
    show_trade_metrics,
)
from .utils import refresh_cache, show_col_desc


def app():
    st.set_page_config(
        page_title="Trade Stats Dashboard",
        page_icon="📈",
        layout="wide",
    )

    # Load configuration and setup
    cfg, pro, accounts, datadirs, index_funcs = load_config()

    # Setup authentication
    setup_authentication(cfg)

    # Refresh cache
    refresh_cache(datadirs)

    # Sort accounts by modification time
    accounts = sort_accounts_by_mtime(accounts, datadirs)

    # Setup benchmark accounts
    benchmark_accounts = list(index_funcs.keys()) + accounts
    benchmark_accounts.append("Custom Symbol")
    benchmark_idx = len(index_funcs) + 1

    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    # Account selection
    def check_account_widget(accounts):
        if "account" not in st.session_state:
            return False
        return all(elem in accounts for elem in st.session_state.account)

    def check_benchmark_widget(benchmark_accounts):
        if "benchmark" not in st.session_state:
            return False
        return st.session_state.benchmark in benchmark_accounts

    if st.session_state.get("swap_once"):
        account = st.session_state.benchmark
        if len(st.session_state.account) > 0:
            benchmark = st.session_state.account[0]
        else:
            benchmark = accounts[1]
        st.session_state.account = [account]
        st.session_state.benchmark = benchmark
        st.session_state["swap_once"] = False
    else:
        st.session_state.account = st.session_state.get("account", [accounts[0]])
        st.session_state.benchmark = st.session_state.get(
            "benchmark", benchmark_accounts[benchmark_idx]
        )

    if not check_account_widget(accounts):
        st.warning("Account not found, reset to default account")
        st.session_state.account = [accounts[0]]

    selected_accounts = st.sidebar.multiselect(
        "Select Account", accounts, key="account"
    )

    if len(selected_accounts) > 1:
        account = "Combined"
    elif len(selected_accounts) == 1:
        account = selected_accounts[0]
    else:
        selected_accounts = [accounts[0]]
        account = selected_accounts[0]

    def swap_account_benchmark():
        st.session_state["swap_once"] = True

    st.sidebar.button("  ↕  ", on_click=swap_account_benchmark)

    if not check_benchmark_widget(benchmark_accounts):
        st.warning("Benchmark not found, reset to default benchmark")
        st.session_state.benchmark = benchmark_accounts[benchmark_idx]

    benchmark = st.sidebar.selectbox(
        "Select Benchmark", benchmark_accounts, key="benchmark"
    )

    if benchmark == "Custom Symbol":
        benchmark = st.sidebar.text_input("Benchmark Symbol", "MSFT")

    bm_ratio = st.sidebar.selectbox("Set Benchmark Leverage", [1, 2, 3, 4, 5], 0)

    if st.session_state.get("swap_once"):
        st.rerun()

    # Load investors data
    if len(selected_accounts) > 1:
        investors = None
    else:
        if os.path.exists("investors.csv"):
            investors = pd.read_csv("investors.csv")
            investors["date"] = pd.to_datetime(investors["date"])
            investors = investors.sort_values("date")
            investors = investors[investors["account"].isin(selected_accounts)]
            if len(investors) == 0:
                investors = None
        else:
            investors = None

    st.header("%s Performance Stats" % (account if cfg is not None else "Strategy"))
    st.markdown("""---""")

    # Load returns and benchmark data
    raw_returns = load_returns(selected_accounts, datadirs)
    rebate_threshold = 0.01 / len(selected_accounts)
    returns = adjust_rebate(raw_returns, rebate_threshold)
    # max_principle = calculate_max_principle_series(returns)
    bm_returns = load_benchmark(benchmark, index_funcs, datadirs)

    if bm_returns is not None:
        bm_returns["returns"] *= bm_ratio

    # Load trade data
    trades = load_trades(selected_accounts, datadirs)
    rts = load_round_trips(selected_accounts, datadirs)
    slippage = load_slippage(selected_accounts, datadirs)

    # Load investor returns
    investor_returns = load_investor_returns(investors, returns)

    # Period selection
    years = list(returns.index.year.unique())
    years.sort(reverse=True)
    year = years[0]

    periods = [
        "Year To Date",
        "Since Inception",
        "Custom Year Range",
        "Custom Date Range",
    ]
    with st.sidebar:
        period = st.selectbox("Select Period", periods, 1 if cfg is None else 0)

        if period == "Year To Date":
            returns = adjust_rebate(returns[returns.index.year == year])
        elif period == "Since Inception":
            returns = adjust_rebate(returns)
        elif period == "Custom Year Range":
            start_year = st.text_input("Start Year", returns.index[-1].date().year)
            end_year = st.text_input("End Year", returns.index[-1].date().year)
            if start_year > end_year:
                st.error("Error: end year should not be earlier than start year.")
            else:
                returns = adjust_rebate(returns[start_year:end_year])
        elif period == "Custom Date Range":
            start_date = st.date_input("Start Date", datetime.date(year, 1, 2))
            end_date = st.date_input("End Date", returns.index[-1].date())
            if start_date > end_date:
                st.error("Error: end date should not be earlier than start date.")
            else:
                returns = adjust_rebate(
                    returns[
                        (returns.index.date >= start_date)
                        & (returns.index.date <= end_date)
                    ]
                )
        else:
            returns = adjust_rebate(returns[returns.index.year == period])

    start_date = returns.index.date[0]
    end_date = returns.index.date[-1]

    # max_principle = max_principle[
    #     (max_principle.index.date >= start_date) & (max_principle.index.date <= end_date)
    # ]

    if bm_returns is not None:
        bm_returns = adjust_rebate(
            bm_returns[
                (bm_returns.index.date >= start_date)
                & (bm_returns.index.date <= end_date)
            ]
        )

    # # Recalculate investor returns for the selected period
    # for investor, ireturns in investor_returns.items():
    #     filtered_returns = ireturns[
    #         (ireturns.index.date >= start_date) & (ireturns.index.date <= end_date)
    #     ]
    #     # Only process if there's actual data in the filtered range
    #     if not filtered_returns.empty:
    #         ireturns = return_stats(filtered_returns)
    #         if ireturns is not None:
    #             investor_returns[investor] = ireturns.sort_index(ascending=False)
    #     else:
    #         # Remove investors with no data in the selected range
    #         investor_returns[investor] = None

    # Filter trade data by date range
    if trades is not None:
        if "date" in trades.columns:
            trades = trades.set_index("date")
        elif "datetime" in trades.columns:
            trades = trades.set_index("datetime")
        elif "timestamp" in trades.columns:
            trades["timestamp"] = trades["timestamp"].apply(
                lambda x: pd.Timestamp(x).tz_localize(None)
            )
            trades = trades.set_index("timestamp")

    if trades is not None:
        trades = trades[
            (trades.index.date >= start_date) & (trades.index.date <= end_date)
        ]
    if rts is not None:
        rts = rts[(rts.index.date >= start_date) & (rts.index.date <= end_date)]
    if slippage is not None:
        slippage = slippage[
            (slippage.index.date >= start_date) & (slippage.index.date <= end_date)
        ]

    if trades is not None and len(trades) == 0:
        trades = None
    if rts is not None and len(rts) == 0:
        rts = None
    if slippage is not None and len(slippage) == 0:
        slippage = None

    if bm_returns is None:
        bm_returns = returns.copy()
        bm_returns.loc[:, :] = 0.0

    returns["benchmark_cum_returns"] = bm_returns["cum_returns"]
    returns["benchmark_underwater"] = bm_returns["underwater"]

    # Generate drawdown tables
    drawdowns = gen_drawdown_table(returns["returns"], 10)
    nan_rows = drawdowns["Duration"].isna()
    drawdowns.loc[nan_rows, "Duration"] = (
        returns.index[-1] - drawdowns.loc[nan_rows, "Peak date"]
    ).dt.days
    drawdowns["Peak date"] = drawdowns["Peak date"].dt.date
    drawdowns["Valley date"] = drawdowns["Valley date"].dt.date
    drawdowns["Recovery date"] = drawdowns["Recovery date"].dt.date
    drawdowns["Net drawdown in %"] *= -1
    drawdowns = drawdowns.rename(columns={"Net drawdown in %": "Drawdown %"})
    drawdowns = drawdowns.dropna(axis=0, how="all")

    bm_drawdowns = gen_drawdown_table(bm_returns["returns"], 10)
    bm_nan_rows = bm_drawdowns["Duration"].isna()
    bm_drawdowns.loc[bm_nan_rows, "Duration"] = (
        bm_returns.index[-1] - bm_drawdowns.loc[nan_rows, "Peak date"]
    ).dt.days
    bm_drawdowns["Peak date"] = bm_drawdowns["Peak date"].dt.date
    bm_drawdowns["Valley date"] = bm_drawdowns["Valley date"].dt.date
    bm_drawdowns["Recovery date"] = bm_drawdowns["Recovery date"].dt.date
    bm_drawdowns["Net drawdown in %"] *= -1
    bm_drawdowns = bm_drawdowns.rename(columns={"Net drawdown in %": "Drawdown %"})

    # Generate return tables
    yearly_return = (
        returns.groupby(pd.Grouper(freq="YE"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    yearly_return.insert(0, "Year", yearly_return.index.year.astype(str))
    yearly_return = yearly_return.reset_index().drop("date", axis=1).set_index("Year")

    bm_yearly_return = (
        bm_returns.groupby(pd.Grouper(freq="YE"))
        .apply(gen_perf)
        .sort_index(ascending=True)
        .dropna()
    )
    bm_yearly_return.insert(0, "Year", bm_yearly_return.index.year.astype(str))
    bm_yearly_return = (
        bm_yearly_return.reset_index().drop("date", axis=1).set_index("Year")
    )

    monthly_return = (
        returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    monthly_return.insert(
        0,
        "Timespan",
        monthly_return.index.year.astype(str)
        + "-"
        + monthly_return.index.month.map("{:02}".format),
    )
    monthly_return = (
        monthly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )
    monthly_return = monthly_return.sort_index()

    bm_monthly_return = (
        bm_returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    bm_monthly_return.insert(
        0,
        "Timespan",
        bm_monthly_return.index.year.astype(str)
        + "-"
        + bm_monthly_return.index.month.map("{:02}".format),
    )
    bm_monthly_return = (
        bm_monthly_return.reset_index()
        .drop("date", axis=1)
        .set_index("Timespan")
        .sort_index()
    )

    weekly_return = (
        returns.groupby(pd.Grouper(freq="W"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    weekly_return.insert(
        0,
        "Timespan",
        weekly_return.index.isocalendar().year.astype(str)
        + " Week "
        + weekly_return.index.isocalendar().week.astype(str),
    )
    weekly_return = (
        weekly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )

    bm_weekly_return = (
        bm_returns.groupby(pd.Grouper(freq="W"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    bm_weekly_return.insert(
        0,
        "Timespan",
        bm_weekly_return.index.isocalendar().year.astype(str)
        + " Week "
        + bm_weekly_return.index.isocalendar().week.astype(str),
    )
    bm_weekly_return = (
        bm_weekly_return.reset_index().drop("date", axis=1).set_index("Timespan")
    )

    # Calculate underlying breakdowns
    ul_breakdown = None
    slippage_breakdown = None
    if trades is not None:
        turnover_col_name = "proceeds" if "proceeds" in trades.columns else "value"

        trades["underlying"] = trades.symbol.apply(
            lambda x: x.split("_")[0]
            if "_" in x
            else "".join([i for i in x if not i.isdigit()])
        )
        ul_breakdown = trades.groupby("underlying").agg(
            roundtrips=pd.NamedAgg(column="pnl", aggfunc="count"),
            total_pnl=pd.NamedAgg(column="pnl", aggfunc="sum"),
            total_turnover=pd.NamedAgg(
                column=turnover_col_name, aggfunc=lambda x: x.abs().sum()
            ),
        )
        ul_breakdown["pnl_ratio"] = (
            ul_breakdown["total_pnl"] / ul_breakdown["total_turnover"]
        )
        ul_breakdown = ul_breakdown.sort_values("total_pnl", ascending=False)

        if slippage is not None:
            slippage["underlying"] = slippage.symbol.apply(
                lambda x: x.split("_")[0]
                if "_" in x
                else "".join([i for i in x if not i.isdigit()])
            )
            slippage_breakdown = slippage.groupby("underlying").agg(
                total_slippage=pd.NamedAgg(column="slippage", aggfunc="sum"),
                total_turnover=pd.NamedAgg(
                    column=turnover_col_name, aggfunc=lambda x: x.abs().sum()
                ),
            )
            slippage_breakdown["slippage_ratio"] = (
                slippage_breakdown["total_slippage"]
                / slippage_breakdown["total_turnover"]
            )

    # Display dashboard
    left_col, right_col = st.columns([5, 2])

    with right_col:
        st.markdown("##### Performance Metrics")
        show_performance_metrics(returns, bm_returns, drawdowns, bm_drawdowns)

        if rts is not None and len(rts) > 0:
            st.write("")
            st.markdown("##### Trade Metrics")
            winners, losers = show_trade_metrics(
                rts, trades, returns, slippage, turnover_col_name
            )

    with left_col:
        if not cfg:
            with st.expander("Account/Benchmark Full Names"):
                records = []
                for acct in selected_accounts:
                    records.append(["Account", acct])
                records.append(["Benchmark", benchmark])
                full_names = (
                    pd.DataFrame.from_records(records, columns=["Type", "Name"])
                    .set_index("Type")
                    .sort_index()
                )
                st.markdown(tabulate(full_names, headers="keys", tablefmt="github"))

        plot_cumulative_returns(returns, bm_returns, bm_ratio)
        plot_underwater(returns, bm_returns)
        plot_yearly_returns(yearly_return, bm_yearly_return)
        plot_monthly_returns_heatmap(returns)
        plot_monthly_returns(monthly_return, bm_monthly_return)
        plot_weekly_returns(weekly_return, bm_weekly_return)

        if trades is not None and len(trades) > 0:
            plot_profit_distribution(ul_breakdown)

        if slippage is not None and len(slippage) > 0:
            plot_slippage_distribution(slippage_breakdown)

    with left_col:
        st.markdown("### Top Drawdowns Table")
        st.dataframe(drawdowns)

        st.markdown("### Returns Tables")
        daily_tab, weekly_tab, monthly_tab, yearly_tab = st.tabs(
            ["Daily", "Weekly", "Monthly", "Yearly"]
        )
        with daily_tab:
            st.markdown("##### Daily Returns")
            st.dataframe(
                returns.drop(["benchmark_cum_returns", "benchmark_underwater"], axis=1)
                .sort_index(ascending=False)
                .style.format(precision=2)
                .format("{:.2%}", subset=["returns", "cum_returns", "underwater"])
            )
            show_col_desc(returns, ["returns"])

        with weekly_tab:
            st.markdown("##### Weekly Returns")
            sub_left_col, sub_right_col = weekly_tab.columns([4, 4])
            with sub_left_col:
                st.dataframe(weekly_return)
            with sub_right_col:
                show_col_desc(weekly_return, ["Return"])
                plot_return_distribution(weekly_return, "weekly")

        with monthly_tab:
            st.markdown("##### Monthly Returns")
            sub_left_col, sub_right_col = monthly_tab.columns([4, 4])
            with sub_left_col:
                st.dataframe(monthly_return)
            with sub_right_col:
                show_col_desc(monthly_return, ["Return"])
                plot_return_distribution(monthly_return, "monthly")

        with yearly_tab:
            st.markdown("### Yearly Returns")
            st.dataframe(yearly_return)

        if rts is not None:
            st.markdown("### Roundtrips Tables")
            winners_tab, losers_tab, rts_tab = st.tabs(["Winners", "Losers", "All"])
            with winners_tab:
                if winners is not None:
                    st.markdown("##### Winners")
                    winners["duration"] = winners["duration"].dt.days
                    st.dataframe(
                        winners.style.format(precision=2).format(
                            "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                        )
                    )
                    show_col_desc(winners, ["pnl_pct", "account_pnl_pct"])
                    show_col_desc(winners, ["duration"], dtype="int")

            with losers_tab:
                if losers is not None:
                    st.markdown("##### Losers")
                    losers["duration"] = losers["duration"].dt.days
                    st.dataframe(
                        losers.style.format(precision=2).format(
                            "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                        )
                    )
                    show_col_desc(losers, ["pnl_pct", "account_pnl_pct"])
                    show_col_desc(losers, ["duration"], dtype="int")

            with rts_tab:
                st.markdown("##### All")
                rts["duration"] = rts["duration"].dt.days
                st.dataframe(
                    rts.style.format(precision=2).format(
                        "{:.2%}", subset=["pnl_pct", "account_pnl_pct"]
                    )
                )

        if trades is not None:
            st.markdown("### Underlying Breakdown")
            if slippage is not None:
                ul_breakdown = ul_breakdown.merge(
                    slippage_breakdown.filter(["total_slippage", "slippage_ratio"]),
                    left_index=True,
                    right_index=True,
                )
                st.dataframe(
                    ul_breakdown.style.format(precision=0)
                    .format("{:.6f}", subset=["pnl_ratio", "slippage_ratio"])
                    .format(
                        "{:,.0f}",
                        subset=["total_pnl", "total_turnover", "total_slippage"],
                    )
                )
            else:
                st.dataframe(
                    ul_breakdown.style.format(precision=0)
                    .format("{:.6f}", subset=["pnl_ratio"])
                    .format("{:,.0f}", subset=["total_pnl", "total_turnover"])
                )

        if investors is not None:
            st.markdown("### Investors Tables")
            names = list(investors["name"].unique())
            # Filter out investors with no data in the selected period
            available_investors = [
                name
                for name in names
                if name in investor_returns and investor_returns[name] is not None
            ]

            if not available_investors:
                st.info("No investor data available for the selected date range.")

            for idx, tab in enumerate(st.tabs(available_investors)):
                investor = available_investors[idx]
                ireturns = investor_returns[investor]
                invested = ireturns.cashflow.sum()

                icashflow = ireturns.filter(["date", "cashflow"]).reset_index()
                icashflow = icashflow.where(icashflow.cashflow != 0).dropna()
                icashflow.columns = ["Date", "Cashflow"]
                icashflow = icashflow.set_index("Date")

                start_value = ireturns.adj_last_eod_value.iloc[-1]
                if np.isnan(start_value):
                    st.markdown("No data for the selected period.")
                    continue

                current_value = ireturns.account_value.iloc[0]

                with tab:
                    isummary_data = [
                        ("Start Value", start_value),
                        ("Net Invested", invested),
                        ("Current Value", current_value),
                        ("PnL", ireturns.today_pnl.sum()),
                        ("Return", ireturns.cum_returns.iloc[0]),
                        ("Annual Return", ep.annual_return(ireturns["returns"])),
                        ("Max Drawdown", ireturns.underwater.min()),
                    ]
                    isummary = pd.DataFrame.from_records(isummary_data).pivot_table(
                        values=1, columns=0, sort=False
                    )
                    isummary.index = [investor]
                    st.markdown("##### Summary")
                    st.dataframe(
                        isummary.style.format(precision=0)
                        .format(
                            "{:.2%}", subset=["Return", "Annual Return", "Max Drawdown"]
                        )
                        .format(
                            "{:,.0f}",
                            subset=[
                                "Start Value",
                                "Net Invested",
                                "Current Value",
                                "PnL",
                            ],
                        )
                    )

                    st.write("")
                    st.markdown("##### Cashflow")
                    st.dataframe(icashflow.style.format("{:,.0f}"))

                    st.write("")
                    st.markdown("##### Daily Returns")
                    st.dataframe(
                        ireturns.style.format(precision=2).format(
                            "{:.2%}", subset=["returns", "cum_returns", "underwater"]
                        )
                    )


if __name__ == "__main__":
    app()
