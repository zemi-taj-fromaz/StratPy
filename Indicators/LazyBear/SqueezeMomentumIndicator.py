import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd

class SMI:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, length  , mult , lengthKC, multKC  ):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  length  , mult , lengthKC, multKC  ))
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
        for length in range(15, 28):
            for mult in [x * 0.1 for x in range(1, 23, 1)]:  # Step by 0  .1
                for lengthKC in range(15, 30, 1):
                    for multKC in range(15, 30, 1):
                        equity = self.calculate( length  , mult , lengthKC, multKC  )
                        print(equity)
                        self.store_result(equity,length  , mult , lengthKC, multKC  )

        self.print_top_results()

    def calculate(self,  length  , mult , lengthKC, multKC ):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        basis = self.timeseries.ta.sma(length)
        dev = mult * self.timeseries["close"].rolling(window=length).std()
        upperBB = basis + dev
        lowerBB = basis - dev

        ma = self.timeseries.ta.sma(lengthKC)
        range = np.maximum(
            self.timeseries["high"] - self.timeseries["low"],
            np.maximum(
                abs(self.timeseries["high"] - self.timeseries["close"].shift(1)),
                abs(self.timeseries["low"] - self.timeseries["close"].shift(1))
            )
        )
        rangema = ta.sma(range, lengthKC)
        upperKC = ma + rangema * multKC
        lowerKC = ma - rangema * multKC

        sqzOn = ((lowerBB > lowerKC) & (upperBB < upperKC)).astype(int)
        sqzOff = ((lowerBB < lowerKC) & (upperBB > upperKC))

        sk = self.timeseries.ta.stoch(stochlen)
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