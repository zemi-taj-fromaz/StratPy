import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq

class NSBB:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length, mult, neutral_width):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length, mult, neutral_width))
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
        for length in range(20, 35):
            for mult in [x * 0.01 for x in range(150, 330, 5)]:  # Step by 0.1
                for neutral_width in [x * 0.01 for x in range(30, 150, 5)]:  # Step by 0.1
                    equity = self.calculate(  length, mult, neutral_width)
                    print(equity)
                    self.store_result(equity,  length, mult, neutral_width)

        self.print_top_results()

    def calculate(self,  length, mult, neutral_width) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        basis = self.timeseries.ta.sma(length)
        dev = mult * self.timeseries["close"].rolling(window = length).std()

        upper = basis + dev
        lower = basis - dev

        neutral_upper = basis + neutral_width * dev
        neutral_lower = basis - neutral_width * dev


        for i in range(length, len(self.timeseries['close'])):
                self.strategy.process(i)

                if(self.timeseries["close"][i] >= neutral_lower[i] and self.timeseries["close"][i] <= neutral_upper[i]):
                    continue

                if(self.timeseries["close"][i] < basis[i]):
                    self.strategy.entry("short", i)
                    continue

                if(self.timeseries["close"][i] > basis[i]):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series