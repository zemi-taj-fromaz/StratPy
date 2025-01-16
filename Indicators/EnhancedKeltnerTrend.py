import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd

class EnhancedKeltnerTrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  atrLen, atrMult, maLen):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  atrLen, atrMult, maLen))
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
        for atrLen in range(10, 22, 1):
            for atrMult in [x * 0.1 for x in range(10, 22, 1)]:  # Step by 0.1
                for maLen in range(4, 19, 1):
                    equity = self.calculate(   atrLen, atrMult, maLen)
                    print(equity)
                    self.store_result(equity,  atrLen, atrMult, maLen)

        self.print_top_results()

    def calculate(self,  atrLen, atrMult, maLen):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        priceBasis = self.timeseries.ta.ema(maLen)
        channelWidth = self.timeseries.ta.atr(atrLen)
        movFactor = ta.ema(channelWidth, maLen) * atrMult
        upperBand = priceBasis + movFactor
        lowerBand = priceBasis - movFactor


        self.timeseries['Long'] = (  self.timeseries["close"] > upperBand.shift(1)).astype(int)
        self.timeseries['Short'] = (   self.timeseries["close"] < lowerBand.shift(1)).astype(int)

        for i in range(max(atrLen, maLen), len(self.timeseries)):
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