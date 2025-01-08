import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class HLTrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, h_length, l_length, h_multi, l_multi):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, h_length, l_length, h_multi, l_multi))
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
        for h_length in range(26, 33):
            for l_length in range(25, 32):
                for h_multi in [x * 0.01 for x in range(90, 110, 2)]:  # Step by 0.1
                    for l_multi in [x * 0.01 for x in range(90, 110, 2)]:  # Step by 0.1
                        equity = self.calculate(h_length, l_length, h_multi, l_multi)
                        print(equity)
                        self.store_result(equity,  h_length, l_length, h_multi, l_multi)

        self.print_top_results()

    def calculate(self,  h_length, l_length, h_multi, l_multi):
        print(f"Calculating for: {h_length}, {l_length} {h_multi}, {l_multi}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries["h"] = self.timeseries["low"].rolling(window=h_length).max() * h_multi

        # Calculate the highest high over l_length periods and multiply by l_multi
        self.timeseries["l"] = self.timeseries["high"].rolling(window=l_length).min() * l_multi

        self.timeseries['Long'] = (
                self.timeseries["high"] >= self.timeseries["h"]
        ).astype(int)
        self.timeseries['Short'] = (
                self.timeseries["low"] < self.timeseries["l"]
        ).astype(int)



        for i in range(max(l_length,h_length), len(self.timeseries['close'])):
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