import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class KalmanRSI:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, rsi_length, kalman_gain, ma_length):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, rsi_length, kalman_gain, ma_length))
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
        for rsi_length in range(25, 42):
            for kalman_gain in [x * 0.01 for x in range(5, 13, 1)]:  # Step by 0.1
                for ma_length in range(2, 10):
                    equity = self.calculate(rsi_length, kalman_gain, ma_length)
                    print(equity)
                    self.store_result(equity, rsi_length, kalman_gain, ma_length)

        self.print_top_results()

    def calculate(self,  rsi_length, kalman_gain, ma_length):
        print(f"Calculating for: {rsi_length}, {kalman_gain} { ma_length}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries["rsi"] = self.timeseries.ta.rsi(length = rsi_length)

        kalman_value = np.nan  # Initialize the Kalman value with NaN
        kalman_values = []  # List to store the calculated Kalman filter values

        for value in self.timeseries["close"]:
            if np.isnan(kalman_value):
                kalman_value = value  # Initialize with the first valid source value
            else:
                kalman_value = kalman_value + kalman_gain * (value - kalman_value)
            kalman_values.append(kalman_value)

        kalman_series = pd.Series(kalman_values, index=self.timeseries.index)
        ema_series = kalman_series.ewm(span=ma_length, adjust=False).mean()

        self.timeseries['Long'] = (
            (kalman_series > ema_series) & (self.timeseries["rsi"] > 50)
        ).astype(int)
        self.timeseries['Short'] = (
                (kalman_series < ema_series) & (self.timeseries["rsi"] < 50)
        ).astype(int)



        for i in range(rsi_length, len(self.timeseries['close'])):
                self.strategy.process(i)

                if(self.timeseries['Short'][i]):
                    self.strategy.entry("short", i)
                    continue

                if(self.timeseries['Long'][i]):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series