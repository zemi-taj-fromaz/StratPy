import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class DemaATR:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, demaLength, lookback, atrFactor):
        heapq.heappush(self.top_results, (equity, demaLength, lookback, atrFactor))
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

        for demaLength in range(1,9):
            for lookback in range(11,17):
                for atrFactor in [x * 0.01 for x in range(120, 200, 2)]:  # Step by 0.1
                    equity = self.calculate(demaLength, lookback, atrFactor)
                    print(equity)
                    self.store_result(equity, demaLength, lookback, atrFactor)
        self.print_top_results()

    def calculate(self, demaLength: int, lookback: int, atrFactor: float = 1.0):
        print("Calculating for : " + str(demaLength) + "," + str(lookback) + "," + str(atrFactor))
        self.timeseries.ta.atr(length= lookback, append=True)
        self.timeseries.ta.dema(length = demaLength, append = True)
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        demaOut = self.timeseries["DEMA_" + str(demaLength)].copy()
        trueRange = atrFactor * self.timeseries["ATRr_" + str(lookback)]

        for i in range(demaLength,len(demaOut)):
                self.strategy.process(i)

                trueRangeUpper = demaOut[i] + trueRange[i]
                trueRangeLower = demaOut[i] - trueRange[i]

                demaOut.loc[i] = demaOut.loc[i - 1]

                if trueRangeLower > demaOut[i]:
                    demaOut.loc[i] = trueRangeLower
                if trueRangeUpper < demaOut[i]:
                    demaOut.loc[i] = trueRangeUpper

                if(demaOut[i] > demaOut[i-1] and demaOut[i - 1] <= demaOut[i - 2]):
                    self.strategy.entry("long", i)

                if(demaOut[i] < demaOut[i-1] and demaOut[i - 1] >= demaOut[i - 2]):
                    self.strategy.entry("short", i)

     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series