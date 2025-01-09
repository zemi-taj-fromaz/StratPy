import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class PPSarOsc:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  start, inc, maxx):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,start, inc, maxx))
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
        inc = 0.001
        for start in range(5, 25):
            for inc in [x * 0.001 for x in range(1, 10, 1)]:  # Step by 0.1
                for maxx in [x * 0.001 for x in range(1, 10, 1)]:  # Step by 0.1
                    equity = self.calculate(  start, inc, maxx)
                    print(equity)
                    self.store_result(equity,start, inc, maxx)

        self.print_top_results()

    def calculate(self, start, inc, maxx):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["sar"] = self.timeseries.ta.sar(start, inc, maxx)
        self.timeseries["oscillator"] = self.timeseries["sar"] - self.timeseries["close"]

        self.timeseries['Long'] = (  self.timeseries["oscillator"] > 0).astype(int)
        self.timeseries['Short'] = (  self.timeseries["oscillator"] < 0).astype(int)

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