import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import statsmodels.api as sm
import pandas as pd


class Plotter:
    def __init__(self, pair_df, open_at=2, close_at=0, n_plots=5):
        self.pair_df = pair_df
        self.ax_counter = 0
        self.open_at = open_at
        self.close_at = close_at
        self.initial_investment = 10000
        self.currency1 = ''
        self.currency2 = ''
        self.fig, self.ax = plt.subplots(nrows=n_plots, figsize=(30, 6*n_plots), dpi=80)

    def set_currencies(self, currency1, currency2):
        self.currency1 = currency1
        self.currency2 = currency2

    def set_initial_investment(self, initial_investment):
        self.initial_investment = initial_investment

    def plot_all(self):
        self.plot_prices()
        self.plot_spread()
        self.plot_zscore()
        self.plot_signals()
        self.plot_returns()

    def plot_prices(self):
        self.__default_plot(metric='prices', title=f'CROSSING PRICES of {self.currency1} x {self.currency2}',
                            is_duplex_plot=True)

    def plot_spread(self):
        self.__default_plot(metric='spread', title=f'SPREAD series ({self.currency1} - {self.currency2} * ratio)')

    def plot_zscore(self):
        self.__default_plot(metric='zscore', title='ZSCORE (quantifies how many standard deviations a '
                                                   'price is away from the mean of its historical price)')

    def plot_signals(self):
        self.__default_plot(metric='signals', title=f'SIGNALS ( if 1, long {self.currency1} and '
                                                    f'short {self.currency2}. if -1, do the opposite. '
                                                    f'If 0 exit positions)')

    def plot_returns(self):
        self.__default_plot(metric='cum_returns', title=f'Dollar cumulative returns.')

    def __default_plot(self, metric, title, is_duplex_plot=False):
        ax = self.ax[self.ax_counter]
        self.ax_counter += 1

        ax.set_title(title)

        if is_duplex_plot:
            series1 = self.pair_df[self.currency1]
            series2 = self.pair_df[self.currency2]

            ratio = sm.OLS(series1, series2).fit().params[0]
            dates = series1.index = pd.to_datetime(series1.index)

            ax.plot(dates, series1)
            ax.plot(dates, series2*ratio)
            ax.legend([f'{self.currency1}', f'{self.currency2}*ratio'], loc="upper left")

        else:
            series = self.pair_df[metric]
            dates = series.index = pd.to_datetime(series.index)
            ax.plot(dates, series)
            ax.legend([metric], loc="upper left")

        tick_positions = []
        tick_labels = []

        for date in dates:
            if date.month == 1 and date.day == 1:
                tick_positions.append(date)
                tick_labels.append(date.strftime('%Y'))

            elif date.day in [10, 20]:
                tick_positions.append(date)
                tick_labels.append(date.strftime('%d'))

            elif date.day == 1:
                tick_positions.append(date)
                tick_labels.append(date.strftime('%b'))

        ax.set_xticks(tick_positions)
        ax.set_xticklabels(tick_labels)
        ax.xaxis.grid(True, which='major')
        # ax.yaxis.set_major_locator(0)

        ax.yaxis.grid(True, which='minor')
        ax.yaxis.grid(True, which='major')

        if metric == 'signals':
            ax.set_yticks([-1, 0, 1], minor=False)

        elif metric == 'zscore':
            open_at = self.open_at
            close_at = self.close_at
            ax.set_yticks([-4, -3, -2, -1, 0, 1, 2, 3, 4], minor=True)
            ax.set_yticks([-open_at, close_at, open_at], minor=False)
            ax.yaxis.grid(True, which='major', color='orange')



    def show(self):
        plt.tight_layout()
        plt.show()
