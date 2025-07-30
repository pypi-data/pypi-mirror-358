import pandas as pd


def extract_roundtrips(df):
    """Extract round-trips from trades dataframe.
    Use itertuples because it's faster than iterrows.
    If trades_df.side.iloc[0] not in ['BUY', 'SELL'],
    then the df is from a broker that has dual positions,
    meaning they track long and short positions separately.

    Args:
        df (DataFrame): Raw trades dataframe with columns:
            - symbol: trading symbol
            - trading_day: trading day for the trade
            - side: trade side string (BUY/SELL for non dual positions, BUY_OPEN/BUY_CLOSE/SELL_OPEN/SELL_CLOSE for dual positions)
            - price: trade price
            - volume: trade volume (always positive)
            - value: trade value (always positive)
            - proceeds: trade proceeds (negative for buying, positive for selling)
                when the column is not present, should be converted from value column (always positive)
            - pnl: realized profit/loss for the trade
            - commission: trade commission (always positive)
                when the column is present, needs to deducted from pnl to get more accurate pnl)

    Returns:
        DataFrame: Round trips with columns:
            - close_dt: close date
            - open_dt: open date
            - symbol: symbol
            - duration: position duration in days
            - pnl: realized profit/loss
            - pnl_pct: profit/loss percentage
            - pos_type: position type (LONG or SHORT)
            - pos_size: position size
    """
    roundtrips = []
    # {(symbol, pos_type): [volume, cost_basis, open_dt, open_commission, accumulated_pnl, accumulated_volume]}
    positions = {}

    # Check if using dual positions
    is_dual = df.side.iloc[0] not in ["BUY", "SELL"]

    # Sort trades by trading_day to ensure proper order
    trades = sorted(df.itertuples(), key=lambda x: x.trading_day)
    current_trading_day = None

    for trade in trades:
        # If trading day changes, process any accumulated trades
        if current_trading_day is not None and trade.trading_day != current_trading_day:
            for pos_key, pos_data in list(positions.items()):
                if len(pos_data) > 4:  # Has accumulated trades
                    symbol, pos_type = pos_key
                    (
                        curr_volume,
                        curr_cost,
                        open_dt,
                        open_commission,
                        acc_pnl,
                        acc_volume,
                    ) = pos_data

                    if (
                        acc_volume > 0
                    ):  # Only create roundtrip if we have closing volume
                        # Calculate percentage return
                        cost_basis = curr_cost * (acc_volume / curr_volume)
                        pnl_pct = acc_pnl / abs(cost_basis)

                        # Round duration to whole days for consistency
                        duration = pd.Timedelta(
                            days=(current_trading_day - open_dt).days
                        )

                        roundtrips.append(
                            {
                                "close_dt": pd.Timestamp(current_trading_day),
                                "open_dt": open_dt,
                                "symbol": symbol,
                                "duration": duration,
                                "pnl": acc_pnl,
                                "pnl_pct": pnl_pct,
                                "pos_type": pos_type,
                                "pos_size": acc_volume,
                            }
                        )

                        # Reset accumulated values
                        positions[pos_key] = positions[pos_key][:4]

        current_trading_day = trade.trading_day
        symbol = trade.symbol
        side = trade.side
        volume = trade.volume
        price = trade.price

        # Determine position type and whether opening or closing
        if is_dual:
            is_opening = side in ["BUY_OPEN", "SELL_OPEN"]
            # For dual positions:
            # - BUY_OPEN/SELL_CLOSE affect long positions
            # - SELL_OPEN/BUY_CLOSE affect short positions
            is_long = side in ["BUY_OPEN", "SELL_CLOSE"]
        else:
            # For simple positions:
            # - BUY opens long or closes short
            # - SELL opens short or closes long
            is_buy = side == "BUY"
            pos_key_long = (symbol, "LONG")
            pos_key_short = (symbol, "SHORT")

            # Check if we have an existing position that this trade would close
            if is_buy and pos_key_short in positions:
                # BUY closing a short position
                is_opening = False
                is_long = False
            elif not is_buy and pos_key_long in positions:
                # SELL closing a long position
                is_opening = False
                is_long = True
            else:
                # Opening a new position
                is_opening = True
                is_long = is_buy

        pos_type = "LONG" if is_long else "SHORT"
        pos_key = (symbol, pos_type)

        if is_opening:
            # Opening or adding to position
            if pos_key not in positions:
                # Store opening commission if available
                open_commission = trade.commission if "commission" in df.columns else 0
                positions[pos_key] = [
                    volume,
                    price * volume,
                    trade.trading_day,
                    open_commission,
                ]
            else:
                curr_volume, curr_cost = positions[pos_key][:2]
                new_volume = curr_volume + volume
                new_cost = curr_cost + price * volume
                positions[pos_key][0] = new_volume
                positions[pos_key][1] = new_cost
        else:
            # Closing position
            if pos_key not in positions:
                # If no matching position to close, this must be opening the opposite position
                opposite_pos_type = "SHORT" if is_long else "LONG"
                opposite_pos_key = (symbol, opposite_pos_type)
                open_commission = trade.commission if "commission" in df.columns else 0
                positions[opposite_pos_key] = [
                    volume,
                    price * volume,
                    trade.trading_day,
                    open_commission,
                ]
                continue

            curr_volume, curr_cost, open_dt, open_commission = positions[pos_key][:4]
            close_volume = min(volume, curr_volume)
            close_ratio = close_volume / curr_volume

            # Calculate PnL and subtract both opening and closing commissions
            pnl = trade.pnl
            if "commission" in df.columns:
                # Subtract both opening and closing commissions proportionally
                pnl -= (open_commission + trade.commission) * close_ratio

            # Check if there's an existing roundtrip for this position on the same day
            same_day_rt_idx = None
            trade_date = trade.trading_day
            for i, rt in enumerate(roundtrips):
                if (
                    rt["symbol"] == symbol
                    and rt["pos_type"] == pos_type
                    and rt["open_dt"] == open_dt
                    and rt["close_dt"] == trade_date
                ):
                    same_day_rt_idx = i
                    break

            if same_day_rt_idx is not None:
                # Update existing roundtrip
                rt = roundtrips[same_day_rt_idx]
                rt["pnl"] += pnl
                rt["pos_size"] += close_volume
                # Update percentage return based on total PnL and cost basis
                total_cost_basis = curr_cost * (rt["pos_size"] / curr_volume)
                rt["pnl_pct"] = rt["pnl"] / abs(total_cost_basis)
                # Use trading day for close date
                rt["close_dt"] = trade.trading_day
            else:
                # Calculate percentage return for this portion
                cost_basis = curr_cost * close_ratio
                pnl_pct = pnl / abs(cost_basis)

                # Round duration to whole days for consistency
                duration = pd.Timedelta(days=(trade.trading_day - open_dt).days)

                # Create new roundtrip
                roundtrips.append(
                    {
                        "close_dt": trade.trading_day,
                        "open_dt": open_dt,
                        "symbol": symbol,
                        "duration": duration,
                        "pnl": pnl,
                        "pnl_pct": pnl_pct,
                        "pos_type": pos_type,
                        "pos_size": close_volume,
                    }
                )

            # Update remaining position if this was a partial close
            if close_volume < curr_volume:
                remaining_ratio = 1 - close_ratio
                # Update position with remaining volume, cost and commission
                positions[pos_key][0] = curr_volume - close_volume
                positions[pos_key][1] = curr_cost * remaining_ratio
                positions[pos_key][3] = open_commission * remaining_ratio
            else:
                del positions[pos_key]
            # If there's excess volume after closing the position,
            # open a new position in the opposite direction
            if volume > close_volume:
                excess_volume = volume - close_volume
                opposite_pos_type = "SHORT" if is_long else "LONG"
                opposite_pos_key = (symbol, opposite_pos_type)
                open_commission = trade.commission if "commission" in df.columns else 0
                positions[opposite_pos_key] = [
                    excess_volume,
                    price * excess_volume,
                    trade.trading_day,
                    open_commission,
                ]

    return pd.DataFrame(roundtrips)
