import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class CasperSupertrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, lengthPeriod, factor, medianLength):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, lengthPeriod, factor, medianLength))
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
        """
        Run the optimization test over the parameter ranges and store the results.
        """
        for lengthPeriod in range(2, 12):
            for factor in [x * 0.01 for x in range(180, 230, 5)]:  # Step by 0.1
                for medianLength in range(4, 15):
                    equity = self.calculate(lengthPeriod, factor, medianLength)
                    print(equity)
                    self.store_result(equity, lengthPeriod, factor, medianLength)

        self.print_top_results()

    def calculate(self,   lengthPeriod, factor, medianLength):
        print(f"Calculating for: {lengthPeriod}, {factor} { medianLength}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries['median'] = self.timeseries['close'].rolling(window=medianLength).quantile(0.5)
        self.timeseries["ATR"] = self.timeseries.ta.atr(length = lengthPeriod)
        self.timeseries["upper"] = self.timeseries["median"] + factor * self.timeseries["ATR"]
        self.timeseries["lower"] = self.timeseries["median"] - factor * self.timeseries["ATR"]

        # Initialize columns
        trend = pd.Series(index=self.timeseries.index, dtype=float)
        direction = pd.Series(index=self.timeseries.index, dtype=int)
        prev_upper_band = self.timeseries["upper"].shift(1)
        prev_lower_band = self.timeseries["lower"].shift(1)
        prev_close = self.timeseries['close'].shift(1)

        # Adjust bands
        lower_band = np.where((self.timeseries["lower"] > prev_lower_band) | (prev_close < prev_lower_band),
                              self.timeseries["lower"], prev_lower_band)
        upper_band = np.where((self.timeseries["upper"] < prev_upper_band) | (prev_close > prev_upper_band),
                              self.timeseries["upper"], prev_upper_band)


        for i in range(medianLength, len(self.timeseries['close'])):
                self.strategy.process(i)

                if i == 0 or np.isnan(self.timeseries["ATR"].iloc[i - 1]):
                    direction.iloc[i] = 1  # Default to upward trend at start
                else:
                    previous_trend = trend.iloc[i - 1]
                    if previous_trend == prev_upper_band.iloc[i]:
                        direction.iloc[i] = -1 if self.timeseries['close'].iloc[i] > upper_band[i] else 1
                    else:
                        direction.iloc[i] = 1 if self.timeseries['close'].iloc[i] < lower_band[i] else -1

                if(direction.iloc[i] == -1):
                    self.strategy.entry("short", i)
                    continue

                if(direction.iloc[i] == 1):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series