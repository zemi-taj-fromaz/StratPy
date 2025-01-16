import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq

## NISAM SIGURSAN JESAM OVO DOOBRO ISPORGRASMIRAO

class DemaAFR:
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

        for demaLength in range(15,21):
            for lookback in range(17,23):
                for atrFactor in [x * 0.1 for x in range(15, 23, 1)]:  # Step by 0.1
                    equity = self.calculate(demaLength, lookback, atrFactor)
                    print(equity)
                    self.store_result(equity, demaLength, lookback, atrFactor)
        self.print_top_results()

    def calculate(self, demaLength: int, lookback: int, atrFactor: float = 1.0):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        atr_afr = self.timeseries.ta.atr(length= lookback)
        dema = self.timeseries.ta.dema(length = demaLength)
        e = atr_afr * atrFactor

        afr = dema
        afr = afr.shift(1)

        atr_factoryHigh = dema + e
        atr_factoryLow = dema - e

        for i in range(max(demaLength, lookback),len(self.timeseries["close"])):
                self.strategy.process(i)

                if (atr_factoryLow[i] > afr[i]):
                    afr[i] = atr_factoryLow[i]
                if (atr_factoryHigh[i] < afr[i]) :
                    afr[i] = atr_factoryHigh[i]

                if(afr[i] < afr[i-1] and afr[i - 1] >= afr[i - 2]):
                    self.strategy.entry("short", i)

                if(afr[i] > afr[i-1] and afr[i - 1] <= afr[i - 2]):
                    self.strategy.entry("long", i)


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series