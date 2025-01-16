import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class RMA:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, alpha, rma_len, sd_mult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,alpha, rma_len, sd_mult))
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
        for alpha in [x * 0.01 for x in range(75, 100, 3)]:  # Step by 0.1
            for rma_len in range(15, 25):
                for sd_mult in [x * 0.01 for x in range(150, 180, 5)]:  # Step by 0.1
                    equity = self.calculate(alpha, rma_len, sd_mult)
                    print(equity)
                    self.store_result(equity, alpha, rma_len, sd_mult)

        self.print_top_results()

    def calculate(self,  alpha, rma_len, sd_mult):
        print(f"Calculating for: {alpha}, {rma_len} { sd_mult}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries["oc2"] = (self.timeseries["open"] + self.timeseries["close"]) / 2.
        initial_sma = self.timeseries["oc2"].rolling(window=rma_len).mean()
        self.timeseries["erma"] = initial_sma

        for i in range(rma_len, len( self.timeseries["close"])):
            self.timeseries["erma"].iat[i] = alpha * initial_sma[i] + (1-alpha) * self.timeseries["erma"].iat[i-1]

        self.timeseries["ohlc4"] = (self.timeseries["open"] + self.timeseries["high"]  + self.timeseries["low"]  + self.timeseries["close"]) / 4.
        self.timeseries["stdev"] = self.timeseries["ohlc4"].rolling(window=rma_len).std() * sd_mult

        self.timeseries['Long'] = (self.timeseries['ohlc4'] > (self.timeseries['erma'] + self.timeseries["stdev"])).astype(int)
        self.timeseries['Short'] = (self.timeseries['ohlc4'] < (self.timeseries['erma'] - self.timeseries["stdev"])).astype(int)

        for i in range(rma_len, len(self.timeseries['close'])):
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