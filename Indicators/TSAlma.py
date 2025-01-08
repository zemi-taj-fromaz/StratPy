import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class TSAlma:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, alma_len, offset, sigma):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, alma_len, offset, sigma))
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
        for alma_len in range(23, 33):
            for offset in [x * 0.01 for x in range(55, 85, 2)]:  # Step by 0.1
                for sigma in [x * 0.1 for x in range(13, 22, 1)]:  # Step by 0.1
                    equity = self.calculate( alma_len, offset, sigma)
                    print(equity)
                    self.store_result(equity,   alma_len, offset, sigma)

        self.print_top_results()

    def calculate(self,  alma_len, offset, sigma) :
        print(f"Calculating for: {alma_len}, {offset}, {sigma}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries['alma'] = self.timeseries.ta.alma(length=alma_len, offset = offset, sigma=sigma)
        self.timeseries['ema'] = self.timeseries.ta.ema(length=alma_len) # Testiraj jos sa HMA i RMA

        self.timeseries['Long'] = (
                (self.timeseries['alma'] > self.timeseries['alma'].shift(1)) &
                (self.timeseries['close'] > self.timeseries['alma']) &
                (self.timeseries['close'] > self.timeseries['ema'])
        ).astype(int)
        self.timeseries['Short'] = (
                (self.timeseries['alma'] < self.timeseries['alma'].shift(1)) &
                (self.timeseries['close'] < self.timeseries['alma']) &
                (self.timeseries['close'] < self.timeseries['ema'])
        ).astype(int)



        for i in range(alma_len, len(self.timeseries['close'])):
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