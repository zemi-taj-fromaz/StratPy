import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math


## PRESKOCI OVO ZASAD; IMA POSLA OKO OTKRIVANJA ZAJEBANCIJE SA THRESHOLDOM ALI TO ZA NEKI DRUGI PUT

class NSMacD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, fast_length, slow_length, signal_smoothing,neutral_zone_threshold ):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, fast_length, slow_length, signal_smoothing,neutral_zone_threshold))
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
        for fast_length in range(3, 22):
            for slow_length in range(max(12, fast_length + 1), 38):
                for signal_smoothing in range(3, 15):
                    for neutral_zone_threshold in range(100, 200, 5):
                        equity = self.calculate(  fast_length, slow_length, signal_smoothing,neutral_zone_threshold)
                        print(equity)
                        self.store_result(equity,  fast_length, slow_length, signal_smoothing,neutral_zone_threshold)

        self.print_top_results()

    def calculate(self, fast_length, slow_length, signal_smoothing,neutral_zone_threshold) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        macd_df = self.timeseries.ta.macd(fast_length, slow_length, signal_smoothing)
        macd_line = macd_df.iloc[:, 0]  # First column
        signal_line = macd_df.iloc[:, 1]  # Third column
        macd_signal_diff = macd_line - signal_line

        is_neutral = np.abs(macd_signal_diff) < neutral_zone_threshold

        for i in range(slow_length, len(self.timeseries['close'])):
                self.strategy.process(i)

                if(is_neutral[i]):
                    print("Neutral state- " + str(macd_signal_diff[i]))
                    continue

                if(macd_line[i] < signal_line[i]):
                    self.strategy.entry("short", i)
                    continue

                if(macd_line[i] > signal_line[i]):
                    self.strategy.entry("long", i)
                    continue

        #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series