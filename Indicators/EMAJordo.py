import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
import math
class EMA:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, alpha, ema_len, atr_len, atr_mult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, ( alpha, ema_len, atr_len, atr_mult))
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
        for alpha in [x * 0.01 for x in range(82, 118, 1)]:  # Step by 0.1
            for ema_len in range(7, 20):
                for atr_len in range(7, 20):
                    for atr_mult in [x * 0.01 for x in range(50, 150, 5)]:  # Step by 0.1
                        equity = self.calculate( alpha, ema_len, atr_len, atr_mult)
                        print(equity)
                        self.store_result(equity, alpha, ema_len, atr_len, atr_mult)

        self.print_top_results()

    def calculate(self, alpha, ema_len, atr_len, atr_mult):
        print(f"Calculating for: {alpha}, {ema_len} { atr_len} {atr_mult}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        halfLength = round(ema_len / 2)
        sqrtLength = round(math.sqrt(ema_len))

        self.timeseries["hmaFull"] = self.timeseries["close"]
        self.timeseries["hmaHalf"] = self.timeseries["close"]
        mult = alpha / (ema_len + 1)
        for i in range(ema_len, len( self.timeseries["close"])):
            self.timeseries["hmaFull"].iat[i] = mult * self.timeseries["close"][i] + (1-mult) * self.timeseries["hmaFull"].iat[i-1]

        mult2 = alpha / (halfLength + 1)
        for i in range(ema_len, len(self.timeseries["close"])):
            self.timeseries["hmaHalf"].iat[i] = mult2 * self.timeseries["close"][i] + (1 - mult2) * self.timeseries["hmaHalf"].iat[i - 1]

        self.timeseries["diff"] = 2* self.timeseries["hmaHalf"] - self.timeseries["hmaFull"]
        self.timeseries["hema"] = self.timeseries["diff"]
        mult3 = alpha / (sqrtLength + 1)
        for i in range(1, len(self.timeseries["close"])):
            self.timeseries["hema"].iat[i] = mult3 * self.timeseries["diff"][i] + (1 - mult3) * self.timeseries["hmaHalf"].iat[i - 1]

        self.timeseries["ATR"] = self.timeseries.ta.atr(length = atr_len) * atr_mult

        self.timeseries['Long'] = (self.timeseries['close'] > (self.timeseries['hema'] + self.timeseries["ATR"])).astype(int)
        self.timeseries['Short'] = (self.timeseries['close'] < (self.timeseries['hema'] - self.timeseries["ATR"])).astype(int)

        for i in range(max(ema_len, atr_len), len(self.timeseries['close'])):
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