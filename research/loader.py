import ccxt
from datetime import datetime
from datetime import timedelta
import pandas as pd


class Loader:

    def __init__(self, exchange: str, fiat: str = 'USDT') -> None:
        exchange_class = getattr(ccxt, exchange)
        self.__client = exchange_class({
            'enableRateLimit': True,
            # 'options': {'defaultType': 'future'},
        })
        self.__fiat = fiat
        self.symbols = self.__get_symbols()
        self.timeframe = str
        self.interval = str

    def __get_symbols(self) -> list:

        # Get all coins from binance #
        self.__markets = self.__client.load_markets()

        # Get only coins that has futures available #
        return [s for s in self.__client.symbols if ':' not in s and f"{s}:{self.__fiat}" in self.__client.symbols]

    def new_historical_data(self, timeframe: str, interval: str) -> pd.DataFrame:
        """
        :param timeframe: e.g. '1d', '4h', '3S', '15m' 
        :type: str
        
        :param interval: e.g. '1 year ago', '3 months ago', '10days ago'
        :type: str
        """

        self.timeframe = timeframe
        self.interval = interval

        return self.__set_data_merge(self.__get_multi_data())

    def __get_multi_data(self) -> list:
        since = self.__get_start_date_from_interval(self.__get_days(self.__get_digit()))
        return [self.__get_single_data(symbol, self.timeframe, since) for symbol in self.symbols]

    def __get_digit(self):
        return [int(s) for s in self.interval.split() if s.isdigit()][0]

    def __get_days(self, digit):
        return digit*365 if 'year' in self.interval else \
               digit*30 if 'month' in self.interval else \
               digit*7 if 'week' in self.interval else \
               digit

    def __get_start_date_from_interval(self, days):
        return int((datetime.now() - timedelta(days=days)).timestamp()) * 1000

    def __get_single_data(self, symbol, timeframe, since) -> pd.DataFrame:
        frame = pd.DataFrame(self.__client.fetch_ohlcv(symbol, timeframe, since=since))
        if len(frame) > 0:
            frame = frame.iloc[:, :6]
            frame.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            frame = frame.set_index('time')
            frame.index = pd.to_datetime(frame.index, unit='ms')
            frame = frame.astype(float)
            return frame

    def __set_data_merge(self, li: list) -> pd.DataFrame:
        return pd.concat(dict(zip(self.symbols, li)), axis=1)
