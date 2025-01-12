import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class DemaEmaCross:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, len_dema, len1st, len2nd):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  len_dema, len1st, len2nd))
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
        for len_dema in range(15, 32):
            for len1st in range(12, 20):
                for len2nd in range(12, 22):
                    equity = self.calculate( len_dema, len1st, len2nd)
                    print(equity)
                    self.store_result(equity, len_dema, len1st, len2nd)

        self.print_top_results()

    def calculate(self,   len_dema, len1st, len2nd):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)
        self.timeseries['dema'] = self.timeseries.ta.dema(length=len_dema)
        self.timeseries["ema1"] = self.timeseries.ta.ema(source = "dema", length = len1st)
        self.timeseries["ema2"] = self.timeseries.ta.ema(source = "dema", length = len2nd)


        self.timeseries['Long'] = (self.timeseries['ema1'] > self.timeseries['ema2']).astype(int)
        self.timeseries['Short'] = (self.timeseries['ema1'] < self.timeseries['ema2']).astype(int)

        for i in range(len2nd, len(self.timeseries)):
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