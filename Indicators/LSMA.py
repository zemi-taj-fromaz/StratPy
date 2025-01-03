import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class LSMA:
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
        for len_lsma in range(55, 72):
            for offset in range(-15, 0, 1):
                    equity = self.calculate(len_lsma, offset)
                    print(equity)
                    self.store_result(equity, len_lsma, offset)

        self.print_top_results()

    def calculate(self, len_lsma: int, offset: int):
        print(f"Calculating for: lsma_length={len_lsma}, offset={offset}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries['LSMA'] = self.timeseries.ta.linreg(length=len_lsma, offset=offset)
        # Entry confirmation source

        for i in range(1, len(self.timeseries['close'])):
                self.strategy.process(i)

                if(self.timeseries['LSMA'][i] < self.timeseries['LSMA'][i-1] and self.timeseries['close'][i] < self.timeseries['LSMA'][i]):
                    self.strategy.entry("short", i)
                    continue

                if(self.timeseries['LSMA'][i] > self.timeseries['LSMA'][i-1] and self.timeseries['close'][i] > self.timeseries['LSMA'][i]):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series