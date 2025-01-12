import pandas_ta as ta
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq

class STC:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []
        self.timeseries["time"] = pd.to_datetime(self.timeseries["time"])
        self.timeseries.set_index("time", inplace=True)

    def store_result(self, equity, demaLength, lookback, atrFactor):
        heapq.heappush(self.top_results, (equity, demaLength, lookback, atrFactor))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)

    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def run_test(self):
        for demaLength in range(4,15):
            for lookback in range(5,19):
                for atrFactor in [x * 0.01 for x in range(110, 250, 2)]:  # Step by 0.1
                    equity = self.calculate(demaLength, lookback, atrFactor)
                    self.store_result(equity, demaLength, lookback, atrFactor)

    def calculate(self, sensitivity: float, length: int, fastLength : int, slowLength : int):
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        fast_ma = self.timeseries.ta.ema(length=fastLength, append=True)
        slow_ma = self.timeseries.ta.ema(length=slowLength, append=True)

        # Calculate trend
        trend = fast_ma - slow_ma
        trend_low = trend.rolling(window=length).min()
        trend_range = trend.rolling(window=length).max() - trend_low

        # Initialize arrays for schaff_value, schaff_ma, pf_ma, and pf
        schaff_value = pd.Series(0, index=self.timeseries.index)
        schaff_ma = pd.Series(0, index=self.timeseries.index)
        pf_ma = pd.Series(0, index=self.timeseries.index)
        pf = pd.Series(0, index=self.timeseries.index)

        uptrend = False
        downtrend = False
        # Iterative calculation
        for i in range(slowLength, len(self.timeseries)):
            self.strategy.process(i)
            if trend_range.iloc[i] > 0:
                schaff_value.iloc[i] = (trend.iloc[i] - trend_low.iloc[i]) / trend_range.iloc[i] * 100
            else:
                schaff_value.iloc[i] = schaff_value.iloc[i - 1] if i > 0 else 0

            schaff_ma.iloc[i] = schaff_value.iloc[i] if i == 0 else schaff_ma.iloc[i - 1] + sensitivity * (schaff_value.iloc[i] - schaff_ma.iloc[i - 1])

            schaff_ma_low = schaff_ma[:i + 1].rolling(window=length).min().iloc[-1]
            schaff_ma_range = schaff_ma[:i + 1].rolling(window=length).max().iloc[-1] - schaff_ma_low

            if schaff_ma_range > 0:
                pf_ma.iloc[i] = (schaff_ma.iloc[i] - schaff_ma_low) / schaff_ma_range * 100
            else:
                pf_ma.iloc[i] = pf_ma.iloc[i - 1] if i > 0 else 0

            pf.iloc[i] = pf_ma.iloc[i] if i == 0 else pf.iloc[i - 1] + sensitivity * (pf_ma.iloc[i] - pf.iloc[i - 1])

            if(pf[i] >= pf[i-1]):
                self.strategy.entry("long", i)
            else:
                self.strategy.entry("short", i)
        # if(pf[i] >= 25 and pf[i-1] < 25 and not uptrend or pf[i] >= 75 and pf[i] < 75 and downtrend):
           #     uptrend = True
           #     downtrend = False
           # if (pf[i] < 75 and pf[i - 1] >= 75 and not downtrend or pf[i] < 25 and pf[i] >= 25 and uptrend):
           #     uptrend = False
           #     downtrend = True

        return self.strategy.equity

        # Simplified example: double the value of each item in the series