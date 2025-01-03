import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class INDI7525:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length, atr_length, mult75, mult25):
        heapq.heappush(self.top_results, (equity, length, atr_length, mult75, mult25))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)

    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def run_test(self):
        for length in range(15,20):
            for atr_length in range(14,19):
                for mult75 in [x * 0.1 for x in range(8, 21, 1)]:  # Step by 0.1
                    for mult25 in [x * 0.1 for x in range(8, 21, 1)]:  # Step by 0.1
                        equity = self.calculate(length, atr_length, mult75, mult25)
                        self.store_result(equity, length, atr_length, mult75, mult25)


    def calculate(self, length: int, atr_length: int, mult75: float, mult25: float):
        print("Calculating for : " + str(length) + "," + str(atr_length) + "," + str(mult75)+ "," + str(mult25))
        self.timeseries['ATR'] = self.timeseries.ta.atr(length= atr_length)

        self.timeseries['Percentile_75'] = self.timeseries['close'].rolling(window=length).quantile(0.75)
        self.timeseries['Percentile_25'] = self.timeseries['close'].rolling(window=length).quantile(0.25)

        self.timeseries['Long'] = self.timeseries['close'] > (self.timeseries['Percentile_75'] + mult75 * self.timeseries['ATR'])
        self.timeseries['Short'] = self.timeseries['close'] < (self.timeseries['Percentile_25'] - mult25 * self.timeseries['ATR'])

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        for i in range(len(self.timeseries['Long'])):
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