import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class LSMAATR:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, len_lsma, offset):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,len_lsma, offset))
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
        for len_lsma in range(75, 94):
            for atr in range(4, 14):
                    equity = self.calculate(len_lsma, atr)
                    print(equity)
                    self.store_result(equity, len_lsma, atr)

        self.print_top_results()

    def calculate(self, len_lsma: int, atr: int):
        print(f"Calculating for: lsma_length={len_lsma}, offset={atr}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries['LSMA'] = self.timeseries.ta.linreg(length=len_lsma, offset=0)
        self.timeseries['ATR'] = self.timeseries.ta.atr(length=atr)
        # Entry confirmation source

        self.timeseries['ATRL'] = self.timeseries['LSMA'] + self.timeseries['ATR']
        self.timeseries['ATRS'] = self.timeseries['LSMA'] - self.timeseries['ATR']

        # Crossover and Crossunder Logic
        self.timeseries['Long'] = (self.timeseries['high'] > self.timeseries['ATRL']).astype(int)
        self.timeseries['Short'] = (self.timeseries['low'] < self.timeseries['ATRS']).astype(int)



        for i in range(len_lsma, len(self.timeseries['close'])):
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