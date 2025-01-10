import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class EnhancedRicky:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, length, atrmult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,   length, atrmult))
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
        self.timeseries["ohlc4"] = (self.timeseries["open"] + self.timeseries["high"] + self.timeseries["low"] + self.timeseries["close"] ) / 4
        for length in range(20, 150, 2):
            for atrmult in [x * 0.1 for x in range(40, 80, 2)]:  # Step by 0.1
                equity = self.calculate( length, atrmult)
                print(equity)
                self.store_result(equity, length, atrmult)

        self.print_top_results()

    def calculate(self,   length, atrmult):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        f = self.timeseries.ta.wma(length / 2)
        s = 2*f - self.timeseries.ta.wma(length)
        hullma = ta.wma(s, math.floor(math.sqrt(length)))
        atrhull = ta.stdev(hullma, 5) * atrmult
        hullplus = hullma + atrhull
        hullminus = hullma - atrhull


        self.timeseries['Long'] = (hullma <  self.timeseries['close']).astype(int)
        self.timeseries['Short'] = (hullminus > self.timeseries['ohlc4']).astype(int)

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