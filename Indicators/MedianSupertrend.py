import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class MedianSupertrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, supertrend_len, multiplier, median_len):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, supertrend_len, multiplier, median_len))
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
        for supertrend_len in range(2, 13):
                for multiplier in [x * 0.01 for x in range(110, 220, 5)]:  # Step by 0.1
                    for median_len in range(5, 16):
                        equity = self.calculate( supertrend_len, multiplier, median_len)
                        print(equity)
                        self.store_result(equity, supertrend_len, multiplier, median_len)

        self.print_top_results()

    def calculate(self, supertrend_len, multiplier, median_len) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        smooth = self.timeseries["close"].rolling(window=median_len).quantile(0.5)

        atr = self.timeseries.ta.atr(length=supertrend_len) * multiplier
        u = smooth + atr
        l = smooth - atr

        st = None
        pt = None
        d = 0
        for i in range(median_len, len(self.timeseries['close'])):
                self.strategy.process(i)
                pt = st
                if(l[i] > l[i-1] or self.timeseries["close"][i-1] < l[i - 1]):
                    l[i] = l[i]
                else:
                    l[i] = l[i - 1]

                if(u[i] < u[i-1] or self.timeseries["close"][i-1] > u[i - 1]):
                    u[i] = u[i]
                else:
                    u[i] = u[i - 1]

                if(atr[i -1] is None):
                    d = 1
                elif(pt is not None and pt == u[i -1]):
                    d = -1 if self.timeseries["close"][i] > u[i] else 1
                else:
                    d = 1 if self.timeseries["close"][i] < l[i] else -1

                st = l[i] if d == -1 else u[i]

                if(d == 1):
                    self.strategy.entry("short", i)
                    continue

                if(d == -1):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series