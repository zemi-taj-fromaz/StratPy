import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd



##neutral state je smece i malo zeza tkao da bolj eizbjegni










class NSSTC:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  k_period, d_period, smooth_k, overbought, oversold):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,   k_period, d_period, smooth_k, overbought, oversold))
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
        for k_period in range(5, 25):
            for d_period in range(1, 15):
                for smooth_k in range(1, 15):
                    for overbought in range(60, 95, 5):
                        for oversold in range(15, 35, 5):
                            equity = self.calculate( k_period, d_period, smooth_k, overbought, oversold)
                            print(equity)
                            self.store_result(equity, k_period, d_period, smooth_k, overbought, oversold)

        self.print_top_results()

    def calculate(self, k_period, d_period, smooth_k, overbought, oversold):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")


        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["hh"] =  self.timeseries["high"].rolling(window=k_period).max()
        self.timeseries["ll"] =  self.timeseries["low"].rolling(window=k_period).min()

        self.timeseries["k"] = (self.timeseries["close"] - self.timeseries["ll"]) / (self.timeseries["hh"] - self.timeseries["ll"]) * 100
        self.timeseries["d"] = self.timeseries.ta.sma(source = "k", length=d_period)

        self.timeseries['Long'] = ( self.timeseries["k"] > self.timeseries["d"]).astype(int)
        self.timeseries['Short'] = ( self.timeseries["d"] < self.timeseries["k"]).astype(int)

        for i in range(max(k_period,d_period), len(self.timeseries)):
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