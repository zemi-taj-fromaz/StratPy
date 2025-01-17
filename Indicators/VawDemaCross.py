import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

from numba import njit

def f_volWDEMA(x_, tr, dema):
    start =  x_.index.start
    stop = x_.index.stop

    length = stop - start

    volatility = np.zeros(length)
    weights = np.zeros(length)
    demas = np.zeros(length)

    for i in range(length):
        true_range = tr[stop - 1 -i]
        volatility[i] = true_range  # Volatility is the True Range
        weights[i] = length + 1 - i
        demas[i] = dema[start + i]

    volatilitySumDEMA = 0.0
    trSumDEMA = 0.0

    # Iterate over the arrays to calculate the sums
    for i in range(len(demas)):
        volatilitySumDEMA += demas[i] * volatility[i] * weights[i]
        trSumDEMA += volatility[i] * weights[i]

    # Return the result of the division
    if trSumDEMA != 0:
        return volatilitySumDEMA / trSumDEMA
    else:
        return 0  # Return 0 if trSumDEMA is 0 to avoid division by zero

class VawDemaCross:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, length1, length2):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length1, length2))
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
        for length1 in range(4, 78):  # Step by 0.1
            for length2 in range(length1 + 1, length1 + 56):  # Step by 0.1
                equity = self.calculate(length1, length2)
                print(equity)
                self.store_result(equity, length1, length2)
        self.print_top_results()

    def calculate(self, length1, length2):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries["dema1"] = self.timeseries.ta.dema(length1)
        self.timeseries["tr1"] = self.timeseries.ta.true_range(length1)
        self.timeseries["dema2"] = self.timeseries.ta.dema(length2)
        self.timeseries["tr2"] = self.timeseries.ta.true_range(length2)

        vwdema1 = self.timeseries["close"].rolling(window=length1).apply(f_volWDEMA, raw=False, kwargs={'tr':self.timeseries["tr1"], 'dema': self.timeseries["dema1"]})
        vwdema2 = self.timeseries["close"].rolling(window=length2).apply(f_volWDEMA, raw=False, kwargs={'tr':self.timeseries["tr2"], 'dema': self.timeseries["dema2"]})

                # Long and Short Conditions
        self.timeseries['Long'] = ( vwdema1 >= vwdema2).astype(int)
        self.timeseries['Short'] = (vwdema1 < vwdema2.shift(1)).astype(int)

        for i in range(max(length1, length2), len(self.timeseries)):
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