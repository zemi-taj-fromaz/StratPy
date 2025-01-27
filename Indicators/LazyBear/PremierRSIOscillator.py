import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd


class Pro:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, lrsi, stochlen , smoothlen ):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  lrsi, stochlen , smoothlen ))
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
        for lrsi in range(15, 28):
            for stochlen in range(15, 28):
                for smoothlen in range(15, 30, 1):
                    equity = self.calculate( lrsi, stochlen , smoothlen )
                    print(equity)
                    self.store_result(equity,lrsi, stochlen , smoothlen)

        self.print_top_results()

    def calculate(self,   lrsi, stochlen , smoothlen):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        r = self.timeseries.ta.rsi(lrsi)

        sk = ta.stoch(r,r,r,stochlen)
        nsk = 0.1 * (sk - 50)
        len = round(math.sqrt(smoothlen))
        ss = ta.ema(ta.ema(nsk,len), len)
        expss = math.exp(ss)
        pso = (expss - 1) / (expss + 1)


        self.timeseries['Long'] = (pso > 0).astype(int)
        self.timeseries['Short'] = (pso < 0).astype(int)

        for i in range(smoothlen , len(self.timeseries)):
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