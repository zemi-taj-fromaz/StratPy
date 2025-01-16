import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math
class EmaZScore:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, emalen, lookback, thresholdL, thresholdS):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, emalen, lookback, thresholdL, thresholdS))
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
        for emalen in range(7, 15):
            for lookback in range(13, 25):
                for thresholdL in [x * 0.1 for x in range(-15, 21, 5)]:  # Step by 0.1
                    for thresholdS in [x * 0.1 for x in range(-25, 1, 5)]:  # Step by 0.1
                        equity = self.calculate(emalen, lookback, thresholdL, thresholdS)
                        print(equity)
                        self.store_result(equity,emalen, lookback, thresholdL, thresholdS)
        self.print_top_results()

    def calculate(self, emalen, lookback, thresholdL, thresholdS):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        ema = self.timeseries.ta.ema(emalen)
        mean = ta.ema(ema, lookback)

        stdDev = ema.rolling(window = lookback).std()
        zScore = (ema - mean) / stdDev

        self.timeseries['Long'] = ( zScore > thresholdL).astype(int)
        self.timeseries['Short'] = ( zScore < thresholdS).astype(int)

        for i in range(max(emalen, lookback), len(self.timeseries)):
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