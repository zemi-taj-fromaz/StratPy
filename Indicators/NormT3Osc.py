import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class NormT3Osc:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, length, vf, norm_period, malen):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  length, vf, norm_period, malen))
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
        for length in range(7, 21):
            for vf in range(30, 70):
             for norm_period in range(30, 70):
                for malen in range(30, 70):
                    equity = self.calculate( length, norm_period)
                    print(equity)
                    self.store_result(equity, length, norm_period)

        self.print_top_results()

    def calculate(self,    length, vf, norm_period, malen):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")


        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["subject"] = self.timeseries.ta.t3(length=length, a = vf)

        self.timeseries["ewma"] = self.timeseries["close"]


        for i in range(length, len(self.timeseries)):
            self.timeseries.loc[i, "ewma"] *= alpha
            for j in range(length):
                weight = math.pow(1 - alpha, j)
                self.timeseries.loc[i, "ewma"] += weight * self.timeseries["ewma"][i-j]

        self.timeseries["lowest"] =  self.timeseries["ewma"].rolling(window=norm_period).min()
        self.timeseries["highest"] =  self.timeseries["ewma"].rolling(window=norm_period).max()

        ewmaOsc = (self.timeseries["ewma"] - self.timeseries["lowest"]) / (self.timeseries["highest"] - self.timeseries["lowest"]) - 0.5

        self.timeseries['Long'] = (ewmaOsc > 0).astype(int)
        self.timeseries['Short'] = (ewmaOsc < 0).astype(int)

        for i in range(length, len(self.timeseries)):
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