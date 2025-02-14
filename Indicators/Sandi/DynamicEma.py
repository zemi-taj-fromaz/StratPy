import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

def DynamicEMA(x_, rma):
    start =  x_.index.start
    stop = x_.index.stop

    fast_end = 2 / 3
    slow_end = 2 / 31

    length = stop - start

    change = math.fabs(x_[start] - x_[stop - 1])
    volatiliy = np.sum(np.abs(x_ - x_.shift(1)))

    efficiency_ratio = change/volatiliy
    smooth_factor = math.pow(efficiency_ratio * (fast_end - slow_end) + slow_end, 2)

    ret = rma.iloc[stop -1] + smooth_factor * (x_[stop - 1] - rma.iloc[stop-1])
    return ret

class DynamicMedianEMA:
    def __init__(self, timeseries, startYear = "2018", condition="ATR"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []
        self.condition = condition

    def store_result(self,equity,length, emalen, sdlen, w1, w2):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length, emalen, sdlen, w1, w2))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)


    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def print_top_results(self):
        top_results = self.get_top_results()
        print("Top Results:")
        for result in top_results:
            params = [f"Equity: {result[0]}"] + [f"Param-{i + 1}: {param}" for i, param in enumerate(result[1:])]
            params.append(f"Trades: {self.strategy.trades}")  # Adding trade count
            print(", ".join(params))
    def run_test(self):
        """
        Run the optimization test over the parameter ranges and store the results.
        """
        for length in range(2, 10):
            for emalen in range(6, 18):
                for sdlen in range(20, 40):
                    for w1 in [x * 0.01 for x in range(12, 50, 2)]:  # Step by 0.1
                        for w2 in [x * 0.01 for x in range(10, 34, 2)]:  # Step by 0.1
                            equity = self.calculate(length, emalen, sdlen, w1, w2)
                            print(equity)
                            self.store_result(equity,length, emalen, sdlen, w1, w2)
        self.print_top_results()

    def calculate(self,  length, emalen, sdlen, w1, w2):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        src = self.timeseries["close"].rolling(window= length + 1).quantile(0.5)
        rma = ta.rma(src, length)

        DynEMA = src.rolling(window=emalen + 1).apply(DynamicEMA, raw = False,  kwargs={'rma':rma})

        haha =  self.timeseries["high"].rolling(window = sdlen).max()
        lolo =  self.timeseries["low"].rolling(window = sdlen).min()

        ranges = haha - lolo

        r1 = DynEMA + ranges * w1
        r2 = DynEMA  - ranges * w2

        # Long and Short Conditions
        self.timeseries['Long'] = ( self.timeseries["close"] > r1).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < r2).astype(int)

        for i in range(max( length, emalen, sdlen), len(self.timeseries)):
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