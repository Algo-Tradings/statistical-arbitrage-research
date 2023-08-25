import pandas as pd
import numpy as np
import statsmodels.tsa.stattools as ts
import statsmodels.api as sm


class Cointegration:
    def __init__(self, cleaned_df: pd.DataFrame):
        self.cleaned_df = cleaned_df
        self.output_df = pd.DataFrame()

    def filter_by_cointegration(self, corr: pd.DataFrame) -> pd.DataFrame:
        self.output_df = self.__select_coint_pairs(corr)
        return self

    def __select_coint_pairs(self, corr: pd.DataFrame) -> pd.DataFrame:
        coint_t, p_value, critical_value = \
            np.vectorize(self.__apply_coint)(corr['currency1'], corr['currency2'])

        corr['coint_t'] = coint_t
        corr['p_value'] = p_value
        corr['criticals'] = critical_value

        return corr[(corr['p_value'] < 0.5) & (corr['coint_t'] < corr['criticals'])
                    ].drop(columns=['p_value', 'coint_t', 'criticals'])

    def __apply_coint(self, currency1, currency2):
        coint_res = ts.coint(self.cleaned_df[currency1], self.cleaned_df[currency2])

        coint_t = coint_res[0]
        p_value = coint_res[1]
        critical_value = coint_res[2][0]

        return coint_t, p_value, critical_value

    def get_results(self):
        return self.output_df
