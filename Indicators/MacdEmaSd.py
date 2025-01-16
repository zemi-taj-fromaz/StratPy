import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class MacdEmaSd:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, lenFast, lenSlow, lookback):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  lenFast, lenSlow, lookback))
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
        for lenFast in range(2, 15):
            for lenSlow in range(lenFast + 1, 40):
                for lookback in range(9, 31):
                    equity = self.calculate( lenFast, lenSlow, lookback)
                    print(equity)
                    self.store_result(equity, lenFast, lenSlow, lookback)

        self.print_top_results()

    def calculate(self,   lenFast, lenSlow, lookback):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        signalLength = 15
        self.timeseries["macd"] = self.timeseries.ta.macd(lenFast, lenSlow, signalLength).iloc[:,0]
        self.timeseries["mean"] = ta.ema(self.timeseries["macd"], lookback)
        stdDevMCD = self.timeseries["macd"].rolling(window = lookback).std()

        zScore = (self.timeseries["macd"] - self.timeseries["mean"]) / stdDevMCD

        self.timeseries['Long'] = (zScore > 1).astype(int)
        self.timeseries['Short'] = (zScore < 0).astype(int)

        for i in range(max(lenSlow, lookback), len(self.timeseries)):
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