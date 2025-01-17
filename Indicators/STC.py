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

    def store_result(self, equity, sensitivity, length, fastLength, slowLength):
        heapq.heappush(self.top_results, (equity, sensitivity, length, fastLength, slowLength))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)

    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def print_top_results(self):
        top_results = self.get_top_results()
        print("Top Results:")
        for result in top_results:
            params = [f"Equity: {result[0]}"] + [f"Param-{i + 1}: {param}" for i, param in enumerate(result[1:])]
            print(", ".join(params))

    def run_test(self):
        for sensitivity in [x * 0.001 for x in range(305, 4355, 10)]:  # Step by 0.1
            for length in range(26,51, 2):
                for fastLength in range(20,40, 2):
                    for slowLength in  range(230,290, 5):  # Step by 0.1
                        equity = self.calculate(sensitivity, length, fastLength, slowLength)
                        print(equity)
                        self.store_result(equity, sensitivity, length, fastLength, slowLength)
        self.print_top_results()


    def calculate(self, sensitivity: float, length: int, fastLength : int, slowLength : int):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        fast_ma = self.timeseries.ta.ema(length=fastLength, append=True)
        slow_ma = self.timeseries.ta.ema(length=slowLength, append=True)

        # Calculate trend
        trend = fast_ma - slow_ma
        trend_low = trend.rolling(window=length).min()
        trend_range = trend.rolling(window=length).max() - trend_low

        schaffValue = np.full_like(trend, np.nan, dtype=float)
        schaffMA = np.full_like(trend, np.nan, dtype=float)

        for i in range(slowLength, len(trend)):
            if(trend_range[i] > 0):
                schaffValue[i] = (trend[i] - trend_low[i]) / trend_range[i] * 100
            else:
                schaffValue[i] = schaffValue[i - 1] if np.isnan(schaffValue[i - 1]) else 0

            schaffMA[i] = schaffValue[i] if np.isnan(schaffMA[i - 1]) else schaffMA[i-1] + sensitivity * (schaffValue[i] - schaffMA[i-1])

        schaffMASeries = pd.Series(schaffMA)

        # Apply rolling operations
        schaffMaLow = schaffMASeries.rolling(window=length).min()
        schaffMaRange = schaffMASeries.rolling(window=length).max() - schaffMaLow

        pfMA = np.full_like(trend, np.nan, dtype=float)
        pf = np.full_like(trend, np.nan, dtype=float)


        for i in range(slowLength, len(trend)):
            if(schaffMaRange[i] > 0):
                pfMA[i] = (schaffMA[i] - schaffMaLow[i]) / schaffMaRange[i] * 100
            else:
                pfMA[i] = pfMA[i - 1] if np.isnan(pfMA[i - 1]) else 0

            pf[i] = pfMA[i] if np.isnan(pf[i - 1]) else pf[i-1] + sensitivity * (pfMA[i-1] - pf[i-1])



        for i in range(slowLength, len(self.timeseries)):
            self.strategy.process(i)

            if(pf[i] >= pf[i-1]):
                self.strategy.entry("long", i)
            else:
                self.strategy.entry("short", i)


        return self.strategy.equity

        # Simplified example: double the value of each item in the series