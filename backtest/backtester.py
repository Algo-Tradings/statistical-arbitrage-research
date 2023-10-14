from research import Researcher
from backtest.plot import Plotter
from backtest import metrics
from backtest import signals
import pandas as pd
import numpy as np

INITIAL_INVESTMENT = 10000


class Backtester:

    def __init__(self, research: Researcher) -> None:
        self.hist_df = research.hist_df
        self.researched_df = research.output_df
        self.results_df = pd.DataFrame()

        self.__settings = {'open_at': 2,
                           'close_at': 0}

    def load_backtests(self):
        self.results_df = pd.read_csv('./data/outputs/backtester.csv', index_col=0
                                      ).sort_values(by='sharperatio', ascending=False)

    def edit_settings(self, open_at=2, close_at=0):
        self.__settings['open_at'] = open_at
        self.__settings['close_at'] = close_at

    def run_backtests(self) -> None:
        rs_df = self.researched_df
        np.vectorize(self.__run_single_backtest)(rs_df.currency1, rs_df.currency2)

    def __run_single_backtest(self, currency1, currency2) -> None:
        pair_df = self.__set_pair_df(currency1, currency2)
        result_df = self.__get_result(pair_df, currency1, currency2)
        self.results_df = (pd.concat([self.results_df, result_df])).sort_values(by='sharperatio', ascending=False)

    def __set_pair_df(self, currency1, currency2):
        prices1 = self.hist_df[currency1].close
        prices2 = self.hist_df[currency2].close
        ratio = self.__select_by_currencies(currency1, currency2)['ratio'].values[0]

        pair_df = pd.DataFrame()
        pair_df[currency1] = prices1
        pair_df[currency2] = prices2
        pair_df["spread"] = metrics.calculate_spread_series(prices1, prices2, ratio)
        pair_df["zscore"] = metrics.calculate_zscore_series(pair_df.spread)
        pair_df.dropna(subset='zscore', inplace=True)

        pair_df['signals'] = signals.set_signals(pair_df.zscore, self.__settings['open_at'],
                                                 self.__settings['close_at'])

        pair_df['log_returns1'] = metrics.calculate_log_return_series(prices1) * pair_df['signals']
        pair_df['log_returns2'] = metrics.calculate_log_return_series(prices2) * -pair_df['signals']
        pair_df['log_returns_total'] = pair_df.log_returns1 + pair_df.log_returns2
        pair_df['simple_returns'] = np.exp(pair_df['log_returns_total']) - 1
        pair_df['dollar_returns'] = pair_df['simple_returns'] * INITIAL_INVESTMENT
        pair_df['cum_returns'] = pair_df['dollar_returns'].cumsum() + INITIAL_INVESTMENT

        return pair_df[pair_df.cum_returns != 0]

    def __select_by_currencies(self, currency1, currency2):
        return self.researched_df[(self.researched_df['currency1'] == currency1) &
                                  (self.researched_df['currency2'] == currency2)]

    def __get_result(self, pair_df, currency1, currency2):
        __returns = pair_df.cum_returns
        __signals = pair_df.signals
        __returns.index = pd.to_datetime(__returns.index)

        n_trades = metrics.calculate_total_trades(__signals)
        if n_trades > 1:
            result_df = pd.DataFrame([n_trades], columns=['n_trades'])
            result_df['sharperatio'] = metrics.calculate_sharpe_ratio(__returns)
            result_df['max_drawdown'] = round(metrics.calculate_max_drawdown(__returns, method='log') * 100, 2)
            result_df['roi'] = round(metrics.calculate_percent_return(__returns) * 100, 2)
            result_df['currency1'] = currency1
            result_df['currency2'] = currency2
            result_df['ratio'] = self.__select_by_currencies(currency1, currency2)['ratio'].values[0]
            result_df['correlation'] = self.__select_by_currencies(currency1, currency2)['correlation'].values[0]

        else:
            result_df = pd.DataFrame()

        return result_df

    def save_outputs(self):
        self.results_df.to_csv('./data/outputs/backtester.csv', index=True)

    def plot(self, currency1, currency2):
        pair_df = self.__set_pair_df(currency1, currency2)
        open_at = self.__settings['open_at']
        close_at = self.__settings['close_at']

        plotter = Plotter(pair_df, open_at=open_at, close_at=close_at, n_plots=5)
        plotter.set_currencies(currency1, currency2)
        plotter.set_initial_investment(INITIAL_INVESTMENT)
        plotter.plot_all()
        plotter.show()

        return pair_df
