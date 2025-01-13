import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

def gaussian_filter(x_, sigma):
    start =  x_.index.start
    stop = x_.index.stop

    length = stop - start + 1

    # Initialize sums
    gaussian_sum = 0.0
    gaussian_weighted_sum = 0.0

    # Apply Gaussian weights
    for i in range(length):
        weight = math.exp(-0.5 * ((i - (length - 1) / 2) / sigma) ** 2)
        gaussian_sum += weight
        gaussian_weighted_sum += x_[stop - i] * weight  # Using the value at index i

    return 0

class RSIZScore:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,length, sigma, atr_length, mult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length, sigma, atr_length, mult))
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
        for periode in range(1, 15):
            for length in range(12, 30):
                for sigma in [x * 0.1 for x in range(12, 28, 1)]:  # Step by 0.1
                    for atr_length in range(7, 21):
                        for mult in [x * 0.1 for x in range(7, 15, 1)]:  # Step by 0.1
                            equity = self.calculate(periode, length, sigma, atr_length, mult)
                            print(equity)
                            self.store_result(equity,periode, length, sigma, atr_length, mult)
        self.print_top_results()





    def calculate(self,  length, sigma, atr_length, mult):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        gaussian_smooth = self.timeseries["close"].rolling(window=length).apply(gaussian_filter, raw=False, kwargs={'sigma':sigma})
        filtered_sma = ta.ema(gaussian_smooth, length)

        atr = self.timeseries.ta.atr(atr_length)

        # Long and Short Conditions
        self.timeseries['Long'] = ( self.timeseries["close"] > filtered_sma + atr * mult).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < filtered_sma - atr * mult).astype(int)

        for i in range(max( length, atr_length), len(self.timeseries)):
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