import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class Zenith:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  length, stdv_length, vwap_length, smaLength):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length, stdv_length, vwap_length, smaLength))
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
        for length in range(3, 30, 2):
            for stdv_length in range(3, 30, 2):
                for vwap_length in range(3, 30, 2):
                    for smaLength in range(3, 30, 2):
                        equity = self.calculate(  length, stdv_length, vwap_length, smaLength)
                        print(equity)
                        self.store_result(equity, length, stdv_length, vwap_length, smaLength)

        self.print_top_results()

    def calculate(self, length, stdv_length, vwap_length, smaLength):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["linregValue"] = ta.linreg(self.timeseries["close"], length=length)
        self.timeseries["deviation"] = self.timeseries["close"] - self.timeseries["linregValue"]

        self.timeseries["stdevValue"] = self.timeseries["deviation"].rolling(window=stdv_length).std()
        self.timeseries["vwapValue"] = ta.vwma(self.timeseries["close"], self.timeseries["volume"], vwap_length)
        self.timeseries["vwapDivergence"] = self.timeseries["close"] - self.timeseries["vwapValue"]

        self.timeseries["dynamicMultiplier"] = self.timeseries["close"].rolling(window = stdv_length).std()

        self.timeseries["combinedValue"] = self.timeseries["stdevValue"] * (1 + self.timeseries["vwapDivergence"] / self.timeseries["dynamicMultiplier"])

        self.timeseries["centeredOscillator"] = self.timeseries["combinedValue"] - ta.sma(self.timeseries["combinedValue"], length = smaLength)
        self.timeseries['Long'] = (  self.timeseries["centeredOscillator"] > 0).astype(int)
        self.timeseries['Short'] = (  self.timeseries["centeredOscillator"] < 0).astype(int)

        for i in range(max(length, stdv_length, vwap_length, smaLength), len(self.timeseries)):
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