import numpy as np
import pandas as pd
from typing import Dict, Callable


def calculate_spread_series(series1: pd.Series, series2: pd.Series, hedge_ratio: float) -> pd.Series:
    """
    Calculates the spread series between two series time hedge ratio on a given time series.
    """
    spread = series1 - series2 * hedge_ratio
    return spread


Z_SCORE_WINDOW = 21


def calculate_zscore_series(spread: pd.Series) -> pd.Series:
    """
    Calculates the spread series between two series time hedge ratio on a given time series.
    """
    mean = spread.rolling(center=False, window=Z_SCORE_WINDOW).mean()
    std = spread.rolling(center=False, window=Z_SCORE_WINDOW).std()
    x = spread.rolling(center=False, window=1).mean()
    return (x - mean) / std


def calculate_total_trades(signals: pd.Series) -> int:
    return len(np.where(np.diff(np.sign(signals)))[0])


def calculate_win_trades(signals, returns):
    pass


def calculate_return_series(series: pd.Series) -> pd.Series:
    """
    Calculates the return series of a given time series.
    The first value will always be NaN.
    """
    shifted_series = series.shift(1, axis=0)
    return series / shifted_series - 1


def calculate_log_return_series(series: pd.Series) -> pd.Series:
    """
    Same as calculate_return_series but with log returns
    """
    return np.log(series.pct_change() + 1)
    # return pd.Series(np.log(series / series.shift(1)))


def calculate_percent_return(series: pd.Series) -> float:
    """
    Takes the first and last value in a series to determine the percent return,
    assuming the series is in date-ascending order
    """
    return series.iloc[-1] / series.iloc[0] - 1


def get_years_past(series: pd.Series) -> float:
    """
    Calculate the years past according to the index of the series for use with
    functions that require annualization
    """
    start_date = series.index[0]
    end_date = series.index[-1]
    return (end_date - start_date).days / 365.25


def calculate_cagr(series: pd.Series) -> float:
    """
    Calculate compounded annual growth rate
    """
    start_price = series.iloc[0]
    end_price = series.iloc[-1]
    value_factor = end_price / start_price
    year_past = get_years_past(series)
    return value_factor ** (1 / year_past) - 1


def calculate_annualized_volatility(return_series: pd.Series) -> float:
    """
    Calculates annualized volatility for a date-indexed return series.
    Works for any interval of date-indexed prices and returns.
    """
    years_past = get_years_past(return_series)
    entries_per_year = return_series.shape[0] / years_past
    return return_series.std() * np.sqrt(entries_per_year)


def calculate_sharpe_ratio(price_series: pd.Series,
                           benchmark_rate: float = 0) -> float:
    """
    Calculates the Sharpe ratio given a price series. Defaults to benchmark_rate
    of zero.
    """
    cagr = calculate_cagr(price_series)
    return_series = calculate_return_series(price_series)
    volatility = calculate_annualized_volatility(return_series)
    return (cagr - benchmark_rate) / volatility


DRAWDOWN_EVALUATORS: Dict[str, Callable] = {
    'dollar': lambda price, peak: peak - price,
    'percent': lambda price, peak: -((price / peak) - 1),
    'log': lambda price, peak: np.log(peak) - np.log(price),
}


def calculate_drawdown_series(series: pd.Series, method: str = 'log') -> pd.Series:
    """
    Returns the drawdown series
    """
    assert method in DRAWDOWN_EVALUATORS, \
        f'Method "{method}" must by one of {list(DRAWDOWN_EVALUATORS.keys())}'

    evaluator = DRAWDOWN_EVALUATORS[method]
    return evaluator(series, series.cummax())


def calculate_max_drawdown(series: pd.Series, method: str = 'log') -> float:
    """
    Simply returns the max drawdown as a float
    """
    return calculate_drawdown_series(series, method).max()

# def calculate_max_drawdown(series: pd.Series) -> float:
#     """
#     Simply returns the max drawdown as a float
#     """
#     s = (series+1).cumprod()
#     return np.ptp(s)/s.max()

# def calculate_max_drawdown(series: pd.Series) -> float:
#     """
#     Simply returns the max drawdown as a float
#     """
#     peaks = np.maximum.accumulate(series)
#     troughs = np.minimum.accumulate(series)
#     drawdowns = (troughs - peaks) / peaks
#     return np.max(drawdowns)
