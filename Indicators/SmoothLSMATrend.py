import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class SmoothLSMATrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length_lsma, smoothing_length):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length_lsma, smoothing_length))
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
        for length_lsma in range(10, 22):
            for smoothing_length in range(2, 13):
                equity = self.calculate( length_lsma, smoothing_length)
                print(equity)
                self.store_result(equity,   length_lsma, smoothing_length)

        self.print_top_results()

    def calculate(self,  length_lsma, smoothing_length) :
        print(f"Calculating for: {length_lsma}, {smoothing_length}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["lsma"] = self.timeseries.ta.linreg(length=length_lsma, offset=0)
        self.timeseries["lsma_offset"] = self.timeseries.ta.linreg(length=length_lsma, offset=1)
 #       print(self.timeseries[['lsma', 'lsma_offset']].tail(10))
        self.timeseries["smoothed_lsma"] = self.timeseries["lsma"].ewm(span=smoothing_length, adjust=False).mean()
        self.timeseries["smoothed_lsma_offset"] = self.timeseries["lsma_offset"].ewm(span=smoothing_length,
                                                                                     adjust=False).mean()
  #      print(self.timeseries[['smoothed_lsma', 'smoothed_lsma_offset']].tail(10))

        slope = self.timeseries["smoothed_lsma"] - self.timeseries["smoothed_lsma_offset"]

        self.timeseries['Long'] = (
                slope > 0
        ).astype(int)
        self.timeseries['Short'] = (
                slope < 0
        ).astype(int)



        for i in range(length_lsma, len(self.timeseries['close'])):
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