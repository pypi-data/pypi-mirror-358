from itertools import groupby

import empyrical as ep
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objs as go
import streamlit as st
from tabulate import tabulate

from .data import calculate_max_principle_series
from .stats import gen_perf, get_period_return, moving_average
from .utils import strfdelta


def show_performance_metrics(returns, bm_returns, drawdowns, bm_drawdowns):
    """Display performance metrics in a table format."""
    summary = [
        [
            "Period",
            "{} days".format((returns.index[-1] - returns.index[0]).days),
            "{} days".format((bm_returns.index[-1] - bm_returns.index[0]).days),
        ],
        [
            "Return",
            "{:.2%}".format(returns["cum_returns"].iloc[-1]),
            "{:.2%}".format(bm_returns["cum_returns"].iloc[-1]),
        ],
        [
            "Annualized",
            "{:.2%}".format(ep.annual_return(returns["returns"])),
            "{:.2%}".format(ep.annual_return(bm_returns["returns"])),
        ],
        [
            "Max Drawdown",
            "{:.2f}%".format(drawdowns.iloc[0, 0]),
            "{:.2f}%".format(bm_drawdowns.iloc[0, 0]),
        ],
        [
            "Sharpe Ratio",
            "{:.3f}".format(ep.sharpe_ratio(returns["returns"])),
            "{:.3f}".format(ep.sharpe_ratio(bm_returns["returns"])),
        ],
        [
            "Sortino Ratio",
            "{:.3f}".format(ep.sortino_ratio(returns["returns"])),
            "{:.3f}".format(ep.sortino_ratio(bm_returns["returns"])),
        ],
        [
            "Volatility",
            "{:.2%}".format(ep.annual_volatility(returns["returns"])),
            "{:.2%}".format(ep.annual_volatility(bm_returns["returns"])),
        ],
        [
            "Calmar Ratio",
            "{:.3f}".format(ep.calmar_ratio(returns["returns"])),
            "{:.3f}".format(ep.calmar_ratio(bm_returns["returns"])),
        ],
        [
            "Tail Ratio",
            "{:.3f}".format(ep.tail_ratio(returns["returns"])),
            "{:.3f}".format(ep.tail_ratio(bm_returns["returns"])),
        ],
        [
            "Gain to Pain Ratio",
            "{:.3f}".format(ep.omega_ratio(get_period_return(returns, freq="ME"))),
            "{:.3f}".format(ep.omega_ratio(get_period_return(bm_returns, freq="ME"))),
        ],
        [
            "Up Days",
            "{:,} ({:.1%})".format(
                sum(returns["returns"] > 0), sum(returns["returns"] > 0) / len(returns)
            ),
            "{:,} ({:.1%})".format(
                sum(bm_returns["returns"] > 0),
                sum(bm_returns["returns"] > 0) / len(bm_returns),
            ),
        ],
        [
            "Down Days",
            "{:,} ({:.1%})".format(
                sum(returns["returns"] < 0), sum(returns["returns"] < 0) / len(returns)
            ),
            "{:,} ({:.1%})".format(
                sum(bm_returns["returns"] < 0),
                sum(bm_returns["returns"] < 0) / len(bm_returns),
            ),
        ],
    ]

    summary_table = tabulate(summary, ["Metric", "Account", "Bench"], tablefmt="github")
    st.markdown(summary_table)


def show_trade_metrics(rts, trades, returns, slippage, turnover_col_name):
    """Display trade metrics in a table format."""
    if rts is None or len(rts) == 0:
        return None, None

    max_principle = calculate_max_principle_series(returns)

    winners = rts[rts.pnl > 0]
    losers = rts[rts.pnl <= 0]

    trade_count = len(rts)
    profit_factor = (
        winners.pnl.sum() / abs(losers.pnl.sum())
        if losers.pnl.sum() != 0
        else float("inf")
    )
    pnl_ratio = (
        (winners.pnl.sum() / len(winners)) / abs(losers.pnl.sum() / len(losers))
        if len(losers) > 0 and losers.pnl.sum() != 0
        else float("inf")
    )
    win_rate = len(winners) / trade_count
    lose_rate = 1 - win_rate
    expected_return_rate = (
        win_rate * winners.account_pnl_pct.mean()
        + (1 - win_rate) * losers.account_pnl_pct.mean()
    )
    kelly = (pnl_ratio * win_rate - lose_rate) / pnl_ratio

    streaks = rts["account_pnl_pct"] > 0
    max_winning_streak = 0
    max_losing_streak = 0
    for key, group in groupby(streaks.values.tolist()):
        group = list(group)
        if sum(group) > 0:
            if len(group) > max_winning_streak:
                max_winning_streak = len(group)
        else:
            if len(group) > max_losing_streak:
                max_losing_streak = len(group)

    turnover = trades[turnover_col_name].abs().sum()
    commission = int(trades.commission.sum())
    rebate = returns["cash_rebate"].sum()
    total_pnl = returns["today_pnl"].sum() + rebate
    # total_pnl = returns["adj_today_pnl"].sum()

    trade_summary = [
        ["Max Principle", "{:,.0f}".format(max_principle.iloc[-1])],
        ["Net Profit", "{:,.0f}".format(total_pnl)],  # with rebate
        ["Cash Rebate", "{:,.0f}".format(rebate)],
        ["No. Trades", trade_count],
        ["Turnover", "{:,.0f}".format(turnover)],
        ["PnL/Turnover", "{:,.2f}‱".format(total_pnl / turnover * 10000)],
        ["Commission", "{:,.0f}".format(commission)],
        ["Commission/Turnover", "{:,.2f}‱".format(commission / turnover * 10000)],
    ]

    if "slippage" in trades.columns or (slippage is not None and len(slippage) > 0):
        if "slippage" in trades.columns:
            slippage = trades

        multiplier = slippage[turnover_col_name] / slippage.price
        slippage["slippage"] = slippage.slippage * multiplier.abs()
        total_slippage = slippage["slippage"].sum()

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
            slippage_breakdown["total_slippage"] / slippage_breakdown["total_turnover"]
        )
        slippage_breakdown = slippage_breakdown.sort_values("total_slippage")

        trade_summary += [
            ["Slippage", "{:,.0f}".format(total_slippage)],
            ["Slippage/Turnover", "{:,.2f}‱".format(total_slippage / turnover * 10000)],
        ]

    trade_summary += [
        [
            "Avg Holding Period",
            strfdelta(pd.to_timedelta(rts.duration).mean(), "%D days %H hrs"),
        ],
        ["Profit Factor", "{:.3f}".format(profit_factor)],
        ["Win Rate", "{:.2%}".format(win_rate)],
        ["Reward/Risk Ratio", "{:.3f}".format(pnl_ratio)],
        ["Expected Return Rate", "{:,.2f}‱".format(expected_return_rate * 10000)],
        ["Kelly Criterion", "{:.2%}".format(kelly)],
        ["Max Winning Streak", max_winning_streak],
        ["Max Losing Streak", max_losing_streak],
        ["Biggest Winner", "{:.2%}".format(winners.account_pnl_pct.max())],
        ["Biggest Loser", "{:.2%}".format(losers.account_pnl_pct.min())],
        ["Winner Median", "{:.2%}".format(winners.account_pnl_pct.median())],
        ["Loser Median", "{:.2%}".format(losers.account_pnl_pct.median())],
    ]

    trade_summary_table = tabulate(
        trade_summary, ["Metric", "Account"], tablefmt="github"
    )
    st.markdown(trade_summary_table)

    return winners, losers


def plot_cumulative_returns(returns, bm_returns, bm_ratio=1):
    """Plot cumulative returns chart."""
    # Create a new dataframe for plotting, so everything starts from 0
    date0 = returns.index[0] - pd.Timedelta(days=1)
    new_row = pd.DataFrame(
        np.zeros((1, len(returns.columns))), columns=returns.columns, index=[date0]
    )
    preturns = pd.concat([new_row, returns], axis=0)

    fig = px.line(
        preturns,
        x=preturns.index,
        y=["cum_returns", "benchmark_cum_returns"],
        title="Cumulative Returns",
        template="seaborn",
    )

    cashflows = returns.loc[returns["cashflow"] != 0, "cashflow"]
    cashflow_x = cashflows.index.tolist()
    cashflow_y = [preturns.loc[date, "cum_returns"] for date in cashflow_x]

    def simplify_amount(amount):
        if abs(amount) >= 1e6:
            return f"${amount / 1e6:.1f}M"
        elif abs(amount) >= 1e3:
            return f"${amount / 1e3:.1f}K"
        else:
            return f"${amount:.2f}"

    cashflow_hover_text = [simplify_amount(amount) for amount in cashflows]
    cashflow_colors = ["green" if amount >= 0 else "red" for amount in cashflows]

    fig.add_trace(
        go.Scatter(
            x=cashflow_x,
            y=cashflow_y,
            name="Cashflows",
            mode="markers",
            hovertext=cashflow_hover_text,
            hoverinfo="text+x+y",
            marker=dict(
                size=10,
                color=cashflow_colors,
            ),
            visible="legendonly",
        )
    )

    ma0 = moving_average(preturns["cum_returns"], 5)
    trace_nav_ma0 = go.Scatter(
        x=preturns.index,
        y=ma0,
        connectgaps=True,
        name="5 days SMA",
        line=dict(dash="dot"),
        visible="legendonly",
    )

    ma1 = moving_average(preturns["cum_returns"], 50)
    trace_nav_ma1 = go.Scatter(
        x=preturns.index,
        y=ma1,
        connectgaps=True,
        name="50 days SMA",
        line=dict(dash="dot"),
    )

    ma2 = moving_average(preturns["cum_returns"], 100)
    trace_nav_ma2 = go.Scatter(
        x=preturns.index,
        y=ma2,
        connectgaps=True,
        name="100 days SMA",
        line=dict(dash="dot"),
    )

    fig.add_trace(trace_nav_ma0)
    fig.add_trace(trace_nav_ma1)
    fig.add_trace(trace_nav_ma2)
    fig.update_traces(connectgaps=True)
    fig["layout"]["legend"]["title"]["text"] = ""
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Returns"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["data"][0]["name"] = "Account"
    fig["data"][1]["name"] = f"Benchmark x {bm_ratio}" if bm_ratio > 1 else "Benchmark"

    st.plotly_chart(fig, use_container_width=True)


def plot_underwater(returns, bm_returns):
    """Plot underwater chart."""
    fig = go.Figure()
    trace = go.Scatter(
        x=returns.index,
        y=returns["underwater"],
        connectgaps=True,
        line_color="red",
        fill="tozeroy",
    )
    bm_trace = go.Scatter(
        x=bm_returns.index,
        y=bm_returns["underwater"],
        connectgaps=True,
        fill="tozeroy",
    )
    fig.add_trace(trace)
    fig.add_trace(bm_trace)
    fig["layout"]["title"] = "Underwater"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Underwater"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["layout"]["template"] = "seaborn"
    fig["data"][0]["name"] = "Account"
    fig["data"][1]["name"] = "Benchmark"

    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_returns_heatmap(returns):
    """Plot monthly returns heatmap."""
    mreturns = (
        returns.groupby(pd.Grouper(freq="ME"))
        .apply(gen_perf)
        .sort_index(ascending=False)
        .dropna()
    )
    mreturns["Return"] *= 100
    mreturns["Year"] = mreturns.index.year
    mreturns["Month"] = mreturns.index.month_name().str[:3]

    mreturns_matrix = mreturns.pivot(
        index="Year", columns="Month", values="Return"
    ).fillna(0)
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    # Handle missing months
    for month in months:
        if month not in mreturns_matrix.columns:
            mreturns_matrix.loc[:, month] = 0
    # Order columns by month
    mreturns_matrix = mreturns_matrix[months]

    fig = px.imshow(
        mreturns_matrix,
        title="Monthly Returns (%)",
        labels=dict(x="Month", y="Year", color="Return"),
        x=mreturns_matrix.columns.tolist(),
        y=mreturns_matrix.index.map(str).tolist(),
        color_continuous_scale="rdylgn",
        color_continuous_midpoint=0,
        aspect="auto",
        text_auto=".2f",
    )
    fig.update_layout(coloraxis_showscale=False)
    fig["layout"]["template"] = "seaborn"

    st.plotly_chart(fig, use_container_width=True)


def plot_return_distribution(returns, period="weekly"):
    """Plot return distribution for a given period."""
    if period == "weekly":
        bins = [-np.inf, -0.05, -0.025, 0, 0.025, 0.05, np.inf]
        labels = ["<-5%", "-5%~-2.5%", "-2.5%~0%", "0%~2.5%", "2.5%~5%", ">5%"]
    elif period == "monthly":
        bins = [-np.inf, -0.1, -0.05, 0, 0.05, 0.1, np.inf]
        labels = ["<-10%", "-10%~-5%", "-5%~0%", "0%~5%", "5%~10%", ">10%"]

    category = pd.cut(returns["Return"], bins=bins, labels=labels)
    counts = category.value_counts()
    fig = px.pie(values=counts, names=counts.index.astype(str))
    st.plotly_chart(fig, use_container_width=True)


def plot_yearly_returns(yearly_return, bm_yearly_return):
    """Plot yearly returns bar chart."""
    fig = go.Figure(
        data=[
            go.Bar(
                name="Account",
                x=yearly_return.index,
                y=yearly_return.Return,
            ),
            go.Bar(
                name="Benchmark",
                x=bm_yearly_return.index,
                y=bm_yearly_return.Return,
            ),
        ],
    )
    fig["layout"]["title"] = "Yearly Returns"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["xaxis"]["tickformat"] = "%Y %b"
    fig["layout"]["yaxis"]["title"]["text"] = "Returns"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["layout"]["template"] = "seaborn"
    st.plotly_chart(fig, use_container_width=True)


def plot_monthly_returns(monthly_return, bm_monthly_return):
    """Plot monthly returns bar chart."""
    fig = go.Figure(
        data=[
            go.Bar(
                name="Account",
                x=monthly_return.index,
                y=monthly_return.Return,
            ),
            go.Bar(
                name="Benchmark",
                x=bm_monthly_return.index,
                y=bm_monthly_return.Return,
            ),
        ],
    )
    fig["layout"]["title"] = "Monthly Returns"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Returns"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["layout"]["template"] = "seaborn"
    st.plotly_chart(fig, use_container_width=True)


def plot_weekly_returns(weekly_return, bm_weekly_return):
    """Plot weekly returns bar chart."""
    fig = go.Figure(
        data=[
            go.Bar(
                name="Account",
                x=weekly_return.index,
                y=weekly_return.Return,
            ),
            go.Bar(
                name="Benchmark",
                x=bm_weekly_return.index,
                y=bm_weekly_return.Return,
            ),
        ],
    )
    fig["layout"]["title"] = "Weekly Returns"
    fig["layout"]["xaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Returns"
    fig["layout"]["yaxis"]["tickformat"] = ",.2%"
    fig["layout"]["template"] = "seaborn"
    st.plotly_chart(fig, use_container_width=True)


def plot_profit_distribution(ul_breakdown):
    """Plot profit distribution by underlying."""
    fig = px.bar(
        ul_breakdown,
        x=ul_breakdown.index,
        y="total_pnl",
        title="Profit Distribution by UL",
        template="seaborn",
    )
    fig["layout"]["xaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "PnL"
    fig["layout"]["yaxis"]["tickformat"] = ",.0f"
    st.plotly_chart(fig, use_container_width=True)


def plot_slippage_distribution(slippage_breakdown):
    """Plot slippage distribution by underlying."""
    fig = px.bar(
        slippage_breakdown,
        x=slippage_breakdown.index,
        y="total_slippage",
        title="Slippage Distribution by UL",
        template="seaborn",
    )
    fig["layout"]["xaxis"]["autorange"] = "reversed"
    fig["layout"]["xaxis"]["title"]["text"] = ""
    fig["layout"]["yaxis"]["title"]["text"] = "Slippage"
    fig["layout"]["yaxis"]["tickformat"] = ",.0f"
    st.plotly_chart(fig, use_container_width=True)
