import pandas as pd
import numpy as np


class Correlation:
    def __init__(self, cleaned_df: pd.DataFrame):
        self.cleaned_df = cleaned_df

    def get_log_correlation(self, min_correlation: float) -> pd.DataFrame:
        corr_df = pd.DataFrame(
            self.__get_highest_df(self.__get_unstacked_df(self.__get_corr_df(self.__get_log_df(self.cleaned_df))),
                                  min_correlation)).reset_index()
        corr_df.columns = ['currency1', 'currency2', 'correlation']
        return corr_df

    @staticmethod
    def __get_log_df(df: pd.DataFrame) -> pd.DataFrame:
        return np.log(df.pct_change() + 1)

    @staticmethod
    def __get_corr_df(df: pd.DataFrame) -> pd.DataFrame:
        return df.corr()

    @staticmethod
    def __get_unstacked_df(df: pd.DataFrame) -> pd.DataFrame:
        return df.unstack().drop_duplicates()

    @staticmethod
    def __get_highest_df(df: pd.DataFrame, min_correlation: float) -> pd.DataFrame:
        return df[(df < 1) & (df >= min_correlation)]
