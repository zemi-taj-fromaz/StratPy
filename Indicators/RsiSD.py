import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class RsiSD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length, sdlen):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length, sdlen))
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
        for length in range(12, 44):
            for sdlen in range(19, 58):
                equity = self.calculate(  length, sdlen)
                print(equity)
                self.store_result(equity,  length, sdlen)

        self.print_top_results()

    def calculate(self,length, sdlen) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        rsi = self.timeseries.ta.rsi(length)

        atr = rsi.rolling(window = sdlen).std()

        u = rsi + atr
        d = rsi - atr

        # Crossover and Crossunder Logic
        self.timeseries['Long'] = (d > 50).astype(int)
        self.timeseries['Short'] = (rsi < 50).astype(int)



        for i in range(max(length, sdlen), len(self.timeseries['close'])):
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