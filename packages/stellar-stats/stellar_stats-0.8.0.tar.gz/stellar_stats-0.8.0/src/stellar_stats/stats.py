from functools import partial

import empyrical as ep
import numpy as np
import pandas as pd

cum_returns = ep.cum_returns

annual_return = ep.annual_return

net_asset_values = partial(ep.cum_returns, starting_value=1.0)


def get_max_drawdown_underwater(underwater):
    """
    Determines peak, valley, and recovery dates given an 'underwater'
    DataFrame.
    """

    valley = underwater.idxmin()  # end of the period
    # Find first 0
    peak = underwater[:valley][underwater[:valley] == 0].index[-1]
    # Find last 0
    try:
        recovery = underwater[valley:][underwater[valley:] == 0].index[0]
    except IndexError:
        recovery = np.nan  # drawdown not recovered
    return peak, valley, recovery


def get_top_drawdowns(returns, top=10):
    returns = returns.copy()
    df_cum = ep.cum_returns(returns, 1.0)
    running_max = np.maximum.accumulate(df_cum)
    underwater = df_cum / running_max - 1

    drawdowns = []
    for _ in range(top):
        peak, valley, recovery = get_max_drawdown_underwater(underwater)
        # Slice out draw-down period
        if not pd.isnull(recovery):
            underwater.drop(underwater[peak:recovery].index[1:-1], inplace=True)
        else:
            # drawdown has not ended yet
            underwater = underwater.loc[:peak]

        drawdowns.append((peak, valley, recovery))
        if (len(returns) == 0) or (len(underwater) == 0) or (np.min(underwater) == 0):
            break

    return drawdowns


def gen_drawdown_table(returns, top=10):
    df_cum = ep.cum_returns(returns, 1.0)
    drawdown_periods = get_top_drawdowns(returns, top=top)
    df_drawdowns = pd.DataFrame(
        index=list(range(top)),
        columns=[
            "Net drawdown in %",
            "Peak date",
            "Valley date",
            "Recovery date",
            "Duration",
        ],
    )

    for i, (peak, valley, recovery) in enumerate(drawdown_periods):
        if pd.isnull(recovery):
            df_drawdowns.loc[i, "Duration"] = np.nan
        else:
            df_drawdowns.loc[i, "Duration"] = len(
                pd.date_range(peak, recovery, freq="B")
            )
        df_drawdowns.loc[i, "Peak date"] = peak.to_pydatetime().strftime("%Y-%m-%d")
        df_drawdowns.loc[i, "Valley date"] = valley.to_pydatetime().strftime("%Y-%m-%d")
        if isinstance(recovery, float):
            df_drawdowns.loc[i, "Recovery date"] = recovery
        else:
            df_drawdowns.loc[i, "Recovery date"] = recovery.to_pydatetime().strftime(
                "%Y-%m-%d"
            )
        df_drawdowns.loc[i, "Net drawdown in %"] = (
            (df_cum.loc[peak] - df_cum.loc[valley]) / df_cum.loc[peak]
        ) * 100

    df_drawdowns["Peak date"] = pd.to_datetime(df_drawdowns["Peak date"])
    df_drawdowns["Valley date"] = pd.to_datetime(df_drawdowns["Valley date"])
    df_drawdowns["Recovery date"] = pd.to_datetime(df_drawdowns["Recovery date"])

    return df_drawdowns


def get_period_return(df, freq):
    def _calc_return(x):
        try:
            initial_value = x["last_eod_value"].iloc[0] + x["cashflow"].sum()
            return (x["account_value"].iloc[-1] - initial_value) / initial_value
        except:
            return np.nan

    return df.groupby(pd.Grouper(freq=freq)).apply(_calc_return).dropna()


def get_underwater(navs):
    running_max = np.maximum.accumulate(navs)
    underwater = -1 * ((running_max - navs) / running_max)
    return underwater


def moving_average(navs, days):
    return navs.rolling(window=days, center=False).mean()


def return_stats(returns):
    if len(returns) == 0:
        return None
    returns_dict = {}
    returns = returns.drop(
        ["cum_returns", "net_asset_values", "underwater"], axis=1, errors="ignore"
    )
    returns_dict["cum_returns"] = ep.cum_returns(returns["returns"])
    nav = ep.cum_returns(returns["returns"], starting_value=1.0)
    returns_dict["net_asset_values"] = nav
    running_max = np.maximum.accumulate(nav)
    returns_dict["underwater"] = -1 * ((running_max - nav) / running_max)
    rdf = pd.concat(returns_dict, axis=1)
    return pd.concat([returns, rdf], axis=1)


def adjust_rebate(returns, rebate_threshold=0.01):
    if "cashflow" not in returns or "today_pnl" not in returns:
        return return_stats(returns)

    rebate_mask = (returns.cashflow > 0) & (
        returns.cashflow / returns.account_value < rebate_threshold
    )
    adjustment = np.where(returns["cashflow"] > 0, returns["cashflow"], 0)
    returns["adj_last_eod_value"] = returns["last_eod_value"] + adjustment
    returns["cash_rebate"] = returns["cashflow"] * rebate_mask
    # Adjust today's pnl as cash rebate is profit
    # This way it will also be considered in the return calculation
    returns["adj_today_pnl"] = returns["today_pnl"] + returns["cash_rebate"]
    returns["returns"] = returns["adj_today_pnl"] / returns["adj_last_eod_value"]
    return return_stats(returns)


def gen_perf(df):
    if len(df) == 0:
        return None
    cashflow = df["cashflow"].sum()
    begin = df["last_eod_value"].iloc[0]
    end = df["account_value"].dropna().iloc[-1]
    change = end - begin - cashflow
    ret = df["returns"] + 1

    return pd.Series(
        [
            begin,
            cashflow,
            end,
            change,
            ret.prod() - 1,
        ],
        index=["Beginning", "Total D/W", "Ending", "Change", "Return"],
    )


def style_returns(df, caption="", sign="", color=None):
    format_dict = {
        "Beginning": "%s{0:,.0f}" % sign,
        "Total D/W": "%s{0:,.0f}" % sign,
        "Ending": "%s{0:,.0f}" % sign,
        "Change": "%s{0:,.0f}" % sign,
        "Return": "{:.2%}",
    }
    if not color:
        color = ["#d65f5f", "#5fba7d"]
    sdf = (
        df.style.format(format_dict)
        .hide(axis="index")
        .set_table_attributes('class="rendered_html"')
        .bar(color=color, subset=["Change", "Return"], align="zero")
    )

    if caption:
        return sdf.set_caption(caption)
    else:
        return sdf


def style_drawdowns(df, caption, color=None):
    format_dict = {
        "Net drawdown": "{:.2f}%",
    }
    if not color:
        color = ["#d65f5f", "#5fba7d"]
    sdf = (
        df.style.format(format_dict)
        .hide_index()
        .set_caption(caption)
        .bar(color=color, subset=["Net drawdown"], align="right")
    )
    return sdf


def adjust_last_eod_value(df):
    return df.last_eod_value + np.where(df.cashflow > 0, df.cashflow, 0)
