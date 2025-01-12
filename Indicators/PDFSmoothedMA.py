import math

import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd

def pdf_ma(x_, variance, mean):
    start =  x_.index.start
    stop = x_.index.stop

    length = stop - start + 1

    x =  1 / (variance * math.sqrt(2 * math.pi)) * math.exp( - math.pow(x_ - mean,2)) / (2* math.pow(variance,2))

    step = math.pi / (length - 1)

    coeffs = np.array()
    for i in range(length):
        factor = i * step
        weight =  1 / (variance * math.sqrt(2 * math.pi)) * math.exp( - math.pow(factor - mean,2)) / (2* math.pow(variance,2))
        coeffs.put(weight)

    sum_weights = coeffs.sum()
    weighted_sum = 0
    for i in range(length):
        weight = coeffs[i]
        src_val = x_[stop - i] if x_[stop - i] is not None else 0
        weighted_sum += weight * src_val

    weighted_avg = weighted_sum / sum_weights
    return weighted_avg
class PDFSmoothedMA:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  period, variance, mean):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, period, variance, mean))
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
        for period in range(2, 30, 1):
            for variance in [x * 0.1 for x in range(10, 20, 1)]:  # Step by 0.1
                for mean in [x * 0.1 for x in range(-8, 8, 1)]:  # Step by 0.1
                        equity = self.calculate(  period, variance, mean)
                        print(equity)
                        self.store_result(equity, period, variance, mean)

        self.print_top_results()

    def calculate(self, period, variance, mean):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        step = math.pi / (period - 1)

        weighted_avg =self.timeseries["close"].rolling(window=period).apply(pdf_ma, raw=False, kwargs={'variance':variance, "mean":mean})
        ema = self.timeseries.ta.ema(period)

        out = (weighted_avg + ema) / 2

        self.timeseries['Long'] = (  out > out.shift(1)).astype(int)
        self.timeseries['Short'] = (  out < out.shift(1)).astype(int)

        for i in range(period, len(self.timeseries)):
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