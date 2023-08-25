from research import Loader
from research import Cleaner
from research import Correlation
from research import Cointegration
from research import Metrics

import pandas as pd


class Researcher:
    def __init__(self) -> None:
        self.hist_df = pd.DataFrame()
        self.output_df = pd.DataFrame()

    def load_research(self) -> None:
        self.hist_df = pd.read_csv('./data/raw/historical_data.csv', header=[0, 1], index_col=0)
        self.output_df = pd.read_csv('./data/outputs/researcher.csv', index_col=0)

    def new_research(self, exchange: str, timeframe: str, interval: str, min_correlation: float) -> None:
        """
        :param exchange: e.g. 'binance', 'kucoin', 'bybit'
        :type: str

        :param timeframe: e.g. '1d', '4h', '3S', '15m'
        :type: str

        :param interval: e.g. '1 year ago', '10days ago', 'datetime'
        :type: str

        :param min_correlation: e.g. '0.83' is 83%
        :type: float
        """
        raw_df = Loader(exchange).new_historical_data(timeframe=timeframe, interval=interval)
        self.hist_df = Cleaner().fill_missing_data(raw_df)
        self.__set_dataframes(min_correlation=min_correlation)

    def __set_dataframes(self, min_correlation: float):
        cleaned_df = Cleaner().get_cleaned_data(self.hist_df)
        corr_df = Correlation(cleaned_df).get_log_correlation(min_correlation=min_correlation)
        coint_df = Cointegration(cleaned_df).filter_by_cointegration(corr_df).get_results()
        output_df = Metrics(cleaned_df).apply_metrics(coint_df).filter_by_crossings().get_results()
        self.output_df = output_df

    def save_outputs(self):
        self.hist_df.to_csv('./data/raw/historical_data.csv', index=True)
        self.output_df.to_csv('./data/outputs/researcher.csv')
