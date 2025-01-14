import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq

class EnhancedKijunSenBase:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, period, mult, kijun_sen_base_period):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, period, mult, kijun_sen_base_period))
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
        for period in range(10, 22):
            for mult in [x * 0.01 for x in range(75, 145, 5)]:  # Step by 0  .1
                for kijun_sen_base_period in range(5, 20):
                    equity = self.calculate( period, mult, kijun_sen_base_period)
                    print(equity)
                    self.store_result(equity,  period, mult, kijun_sen_base_period)

        self.print_top_results()


    def calculate(self,  period, mult, kijun_sen_base_period):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        high = self.timeseries["close"].rolling(window = kijun_sen_base_period).max()
        low = self.timeseries["close"].rolling(window = kijun_sen_base_period).min()

        M7 = (high + low) / 2
        filter = self.timeseries.ta.atr(period) * mult

       # Long and Short Conditions
        self.timeseries['Long'] = (self.timeseries["close"] > M7 + filter).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < M7 - filter).astype(int)

        for i in range(max(period, kijun_sen_base_period), len(self.timeseries['close'])):
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