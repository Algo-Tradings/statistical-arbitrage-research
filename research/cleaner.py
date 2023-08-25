import pandas as pd


class Cleaner:
    @staticmethod
    def fill_missing_data(df: pd.DataFrame) -> pd.DataFrame:
        return df.fillna(method='ffill')

    def get_cleaned_data(self, hist_df: pd.DataFrame) -> pd.DataFrame:
        return self.__remove_young_currencies(self.__get_data_close(hist_df))

    @staticmethod
    def __get_data_close(df: pd.DataFrame) -> pd.DataFrame:
        closes_df = df.loc[:, df.columns.get_level_values(1).isin(['close'])]
        closes_df.columns = closes_df.columns.droplevel(1)
        return closes_df

    @staticmethod
    def __remove_young_currencies(df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(how='any', axis=1)
