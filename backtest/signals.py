import numpy as np
import pandas as pd


def set_signals(series: pd.Series,  open_at: float = 2.0, close_at: float = 0.0) -> pd.Series:

    # Set signals by Trading Conditions
    signals = series.copy()

    for i in range(0, len(series)):
        buy_entry_signal = series.iloc[i] <= -abs(open_at)
        buy_close_signal = (signals.iloc[i-1] == 1) & (series.iloc[i] <= abs(close_at))

        sell_entry_signal = series[i] >= abs(open_at)
        sell_close_signal = (signals.iloc[i-1] == -1) & (series.iloc[i] >= -abs(close_at))

        signals.iloc[i] = 1 if buy_entry_signal or buy_close_signal else -1 if sell_entry_signal or sell_close_signal else 0

    return signals.shift().fillna(0)
    return signals
