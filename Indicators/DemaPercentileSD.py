import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math


class DemaPercentileSD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity,  DemaLen, PerLen, SDlen,EmaLen, per1, per2):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  DemaLen, PerLen, SDlen,EmaLen, per1, per2))
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
        for DemaLen in range(3, 18):
            for PerLen in range(30, 70, 2):
                for SDlen in range(19, 37, 2):
                    for EmaLen in range(40, 110, 2):
                        for per1 in range(55,65, 5):
                            for per2 in range(40,50, 5):
                                equity = self.calculate(  DemaLen, PerLen, SDlen,EmaLen, per1, per2)
                                print(equity)
                                self.store_result(equity, DemaLen, PerLen, SDlen,EmaLen,  per1, per2)

        self.print_top_results()

    def calculate(self, DemaLen, PerLen, SDlen,EmaLen,  per1, per2) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        dema = ta.dema(self.timeseries["high"], DemaLen)

        perUp = dema.rolling(window = PerLen).quantile(per1 * 0.01)
        perDn = dema.rolling(window = PerLen).quantile(per2 * 0.01)

        sd = perDn.rolling(window = SDlen).std()
        sdl = perDn + sd

        self.timeseries['Long'] = ((self.timeseries['close'] > perUp) & (self.timeseries["close"] > sdl)).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < perDn).astype(int)

        for i in range(max(DemaLen, PerLen, SDlen,EmaLen), len(self.timeseries['close'])):
                self.strategy.process(i)

                if( self.timeseries['Short'][i]):
                    self.strategy.entry("short", i)
                    continue

                if( self.timeseries['Long'][i]):
                    self.strategy.entry("long", i)
                    continue

        #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series