import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class FourMACD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  mult_b, mult_y):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,mult_b, mult_y))
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
        for mult_b in range(2, 30, 2):
            for mult_y in range(2, 30, 2):
                equity = self.calculate(  mult_b, mult_y)
                print(equity)
                self.store_result(equity, mult_b, mult_y)

        self.print_top_results()

    def calculate(self, mult_b, mult_y):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # EMA Calculations
        self.timeseries["ema5"] = self.timeseries.ta.ema(length=5)
        self.timeseries["ema8"] = self.timeseries.ta.ema(length=8)
        self.timeseries["ema10"] = self.timeseries.ta.ema(length=10)
        self.timeseries["ema14"] = self.timeseries.ta.ema(length=14)
        self.timeseries["ema16"] = self.timeseries.ta.ema(length=16)
        self.timeseries["ema17"] = self.timeseries.ta.ema(length=17)

        # Differences between EMAs
        self.timeseries["ema17_14"] = self.timeseries["ema17"] - self.timeseries["ema14"]
        self.timeseries["ema17_8"] = self.timeseries["ema17"] - self.timeseries["ema8"]
        self.timeseries["ema10_16"] = self.timeseries["ema10"] - self.timeseries["ema16"]
        self.timeseries["ema5_10"] = self.timeseries["ema5"] - self.timeseries["ema10"]

        # MACD-Like Calculations
        self.timeseries["MACDBlue"] = mult_b * (
            self.timeseries["ema17_14"] - self.timeseries.ta.ema(self.timeseries["ema17_14"], length=5)
        )
        self.timeseries["MACDRed"] = self.timeseries["ema17_8"] - self.timeseries.ta.ema(self.timeseries["ema17_8"], length=5)
        self.timeseries["MACDYellow"] = mult_y * (
            self.timeseries["ema10_16"] - self.timeseries.ta.ema(self.timeseries["ema10_16"], length=5)
        )
        self.timeseries["MACDGreen"] = self.timeseries["ema5_10"] - self.timeseries.ta.ema(self.timeseries["ema5_10"], length=5)


        self.timeseries['Long'] = (  self.timeseries["MACDYellow"] > 0).astype(int)
        self.timeseries['Short'] = (  self.timeseries["MACDGreen"] < 0).astype(int)

        for i in range(20, len(self.timeseries)):
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