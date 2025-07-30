import os
from functools import partial

import tomlkit
import tushare as ts

from .data import load_remote


def load_config(cfg_path="config.toml"):
    """Load configuration from TOML file and setup necessary API clients."""
    if os.path.exists(cfg_path):
        cfg = tomlkit.loads(open(cfg_path).read())
        pro = (
            ts.pro_api(cfg["general"]["tushare_token"])
            if "tushare_token" in cfg["general"]
            else None
        )
    else:
        cfg = None
        pro = None

    # Setup accounts and datadirs
    if cfg and "accounts" in cfg:
        accounts = list(cfg["accounts"].keys())
        datadirs = cfg["accounts"]
    else:
        accounts = [
            d for d in os.listdir(".") if os.path.isdir(d) and not d.startswith(".")
        ]
        datadirs = {d: d for d in accounts}

    # Setup index functions
    index_funcs = {}
    if pro is not None:
        index_funcs = {
            "南华商品指数": partial(pro.index_daily, ts_code="NHCI.NH"),
            "沪深300指数": partial(pro.index_daily, ts_code="000300.SH"),
            "标普500指数": partial(load_remote, "^GSPC", start="2000-01-01"),
            "纳斯达克综指": partial(load_remote, "^IXIC", start="2000-01-01"),
        }

    return cfg, pro, accounts, datadirs, index_funcs


def sort_accounts_by_mtime(accounts, datadirs):
    """Sort accounts by modification time of their returns file."""

    def sort_mtime(x):
        if os.path.exists(f"{datadirs[x]}/returns.csv"):
            path = f"{datadirs[x]}/returns.csv"
        elif os.path.exists(f"{datadirs[x]}/returns.hdf"):
            path = f"{datadirs[x]}/returns.hdf"
        elif os.path.exists(f"{datadirs[x]}/returns.parquet"):
            path = f"{datadirs[x]}/returns.parquet"
        else:
            return 0

        return os.path.getmtime(path)

    accounts.sort(key=sort_mtime, reverse=True)
    return accounts
