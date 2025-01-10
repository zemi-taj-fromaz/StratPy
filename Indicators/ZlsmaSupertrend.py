import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class ZlsmaSupertrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, supLen, multiplier, lagLength):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  supLen, multiplier, lagLength))
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
        for supLen in range(6, 22):
            for multiplier in [x * 0.01 for x in range(250, 350, 5)]:  # Step by 0.1
                for lagLength in range(4, 16):
                    equity = self.calculate( supLen, multiplier, lagLength)
                    print(equity)
                    self.store_result(equity, supLen, multiplier, lagLength)

        self.print_top_results()

    def calculate(self,   supLen, multiplier, lagLength):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        lsma = self.timeseries.ta.linreg(lagLength, 0)
        lsma2 = ta.linreg(lsma, lagLength, 0)

        eq = lsma - lsma2
        zlsma = lsma + eq

        atr = self.timeseries.ta.atr(supLen)
        ub = zlsma + multiplier * atr
        lb = zlsma - multiplier * atr

        d = 1
        pst = None

        for i in range(max(supLen, lagLength) + 1, len(self.timeseries)):
                self.strategy.process(i)

                plb = lb[i-1]
                pub = ub[i-1]

                if(not (lb[i] > plb or self.timseries["close"][i-1] < plb)):
                    lb[i] = plb

                if (not (ub[i] < pub or self.timseries["close"][i - 1] > pub)):
                    lb[i] = plb

                if(pst is not None and pst == pub):
                    d = -1 if self.timeseries["close"][i] > ub[i] else 1
                else:
                    d = 1 if self.timeseries["close"][i] < lb[i] else -1

                if(d < 0):
                    self.strategy.entry("short", i)
                    continue

                if(d > 0):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series