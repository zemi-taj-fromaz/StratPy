import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class Ewma:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, lenx, atr_length, smoothingLength, volatilityFactor):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  lenx, atr_length, smoothingLength, volatilityFactor))
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
        for lenx in range(12, 50):
            for atr_length in range(10, 23):
                for smoothingLength in range(2, 13):
                    for volatilityFactor in [x * 0.1 for x in range(7, 16, 1)]:  # Step by 0.1
                        equity = self.calculate( lenx, atr_length, smoothingLength, volatilityFactor)
                        print(equity)
                        self.store_result(equity, lenx)
        self.print_top_results()

    def calculate(self,   lenx, atr_length, smoothingLength, volatilityFactor):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        volatility = self.timeseries.ta.atr(atr_length)
        adjusted_len = lenx * (1 + (volatilityFactor * (volatility / self.timeseries["close"])))

        smoothing_factor = 2 / (adjusted_len + 1)

        ewma = np.zeros_like(self.timeseries["close"])
        for i in range(len(adjusted_len)):
            if(smoothing_factor[i] is None):
                continue
            ewma[i] = smoothing_factor[i] * self.timeseries["close"][i] + ( 1 - smoothing_factor[i]) * ewma[i - 1]

        smoothed_ewma = ta.sma(ewma, smoothingLength)


        self.timeseries['Long'] = (smoothed_ewma > smoothed_ewma.shift(1)).astype(int)
        self.timeseries['Short'] = (smoothed_ewma < smoothed_ewma.shift(1)).astype(int)

        for i in range(lenx, len(self.timeseries)):
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