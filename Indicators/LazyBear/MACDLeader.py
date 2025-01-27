import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd

def calc_wima(x_, lengthz):
    start =  x_.index.start
    stop = x_.index.stop
    length = stop - start

    return (x_[stop -1] + x_[stop - 2] * (lengthz - 1)) / lengthz

class MACDLeader:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, shortLength  , longLength, sigLength   ):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, shortLength  , longLength, sigLength  ))
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
        for shortLength in range(15, 28):
            for longLength in range(15, 28):
                for sigLength in range(15, 28):
                    equity = self.calculate(shortLength  , longLength, sigLength    )
                    print(equity)
                    self.store_result(equity,shortLength  , longLength, sigLength    )

        self.print_top_results()

    def calculate(self,shortLength  , longLength, sigLength  ):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        src = self.timeseries["close"].copy()

        sema = self.timeseries.ta.ema(shortLength)
        lema = self.timeseries.ta.ema(longLength)

        i1 = sema + ta.ema(src - sema, shortLength)
        i2 = lema + ta.ema(src - lema, longLength)

        macdl = i1 - i2
        macd = sema - lema

        self.timeseries['Long'] = (hist > 0).astype(int)
        self.timeseries['Short'] = (hist < 0).astype(int)

        for i in range(max( slowLength, signalLength , lengthz) , len(self.timeseries)):
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