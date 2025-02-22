import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class CasperSupertrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, lengthPeriod, factor, medianLength):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, lengthPeriod, factor, medianLength))
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
        for lengthPeriod in range(2, 12):
            for factor in [x * 0.01 for x in range(180, 230, 5)]:  # Step by 0  .1
                for medianLength in range(4, 15):
                    equity = self.calculate(lengthPeriod, factor, medianLength)
                    print(equity)
                    self.store_result(equity, lengthPeriod, factor, medianLength)

        self.print_top_results()

    def calculate(self,   lengthPeriod, factor, medianLength):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        source = self.timeseries['close'].rolling(window=medianLength).quantile(0.5)

        volatility = self.timeseries.ta.atr(length = lengthPeriod)

        u = source + factor * volatility
        l = source - factor * volatility

        trend = None
        previousTrend = None
        d = 0
        for i in range(max(lengthPeriod, medianLength), len(self.timeseries['close'])):
                self.strategy.process(i)
                previousTrend = trend

                if(l[i] > l[i-1] or self.timeseries["close"][i-1] < l[i - 1]):
                    l[i] = l[i]
                else:
                    l[i] = l[i - 1]

                if(u[i] < u[i-1] or self.timeseries["close"][i-1] > u[i - 1]):
                    u[i] = u[i]
                else:
                    u[i] = u[i - 1]

                if(volatility[i -1] is None):
                    d = 1
                elif(previousTrend is not None and previousTrend == u[i -1]):
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