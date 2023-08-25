import pandas as pd
import numpy as np
import statsmodels.api as sm


class Metrics:
    def __init__(self, cleaned_df: pd.DataFrame):
        self.cleaned_df = cleaned_df
        self.output_df = pd.DataFrame()

    def apply_metrics(self, coint_df: pd.DataFrame):
        (ratio, zero_crossings) = np.vectorize(
            self.__metrics_by_pairs)(coint_df['currency1'], coint_df['currency2'])

        coint_df['ratio'] = ratio
        coint_df['zero_crossings'] = zero_crossings
        self.output_df = coint_df
        return self

    def __metrics_by_pairs(self, currency1, currency2):
        (series1, series2) = (self.cleaned_df[currency1], self.cleaned_df[currency2])

        ratio = self.__set_hedge_ratio(series1, series2)
        zero_crossings = self.__get_zero_crossings(series1, series2, ratio)

        return ratio, zero_crossings

    @staticmethod
    def __set_hedge_ratio(series1, series2):
        model = sm.OLS(series1, series2).fit()
        return model.params[0]

    def __get_zero_crossings(self, series1, series2, ratio):
        return len(np.where(np.diff(np.sign(self.__calculate_spread(series1, series2, ratio))))[0])

    @staticmethod
    def __calculate_spread(series1, series2, hedge_ratio):
        return series1 - series2 * hedge_ratio

    def filter_by_crossings(self):
        self.output_df = self.output_df[self.output_df['zero_crossings'] > self.output_df['zero_crossings'].max() / 2
                                        ].sort_values(by='zero_crossings', ascending=False)
        return self

    def get_results(self):
        return self.output_df
