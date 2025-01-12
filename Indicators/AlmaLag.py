import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class AlmaLag:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length))
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
        for length in range(22, 180):
            equity = self.calculate(length)
            print(equity)
            self.store_result(equity, length)

        self.print_top_results()


    def calculate(self, length):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate DEMA
        alma = self.timeseries.ta.alma(length=length)

       # Long and Short Conditions
        self.timeseries['Long'] = ((alma > alma.shift(1)) & (self.timeseries["close"] > alma)).astype(int)
        self.timeseries['Short'] = ((alma < alma.shift(1)) & (self.timeseries["close"] < alma)).astype(int)

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