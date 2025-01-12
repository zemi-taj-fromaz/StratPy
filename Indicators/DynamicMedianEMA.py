import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

def DynamicEMA(x_):
    start =  x_.index.start
    stop = x_.index.stop

    fast_end = 2 / 3
    slow_end = 2 / 31

    length = stop - start + 1

    change = math.fabs(x_[start] - x_[stop])
    volatiliy = np.sum(math.fabs(x_ - x_.shift(1)))

    efficiency_ratio = change/volatiliy
    smooth_factor = math.pow(efficiency_ratio * (fast_end - slow_end) + slow_end, 2)
    rma = ta.rma(x_, length - 1)

    return rma + smooth_factor * (x_ - rma)

class DynamicMedianEMA:
    def __init__(self, timeseries, startYear = "2018", condition="ATR"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []
        self.condition = condition

    def store_result(self,equity,length, emalen, sdlen, atr_length, atr_mult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length, emalen, sdlen, atr_length, atr_mult))
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
        for length in range(2, 10):
            for emalen in range(6, 18):
                for sdlen in range(20, 40):
                    for atr_length in range(7, 21):
                        for atr_mult in [x * 0.1 for x in range(70, 170, 5)]:  # Step by 0.1
                            equity = self.calculate(length, emalen, sdlen, atr_length, atr_mult)
                            print(equity)
                            self.store_result(equity,length, emalen, sdlen, atr_length, atr_mult)
        self.print_top_results()

    def calculate(self,  length, emalen, sdlen, atr_length, atr_mult):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        dwmas = self.timeseries["close"].rolling(window=emalen + 1).apply(DynamicEMA)

        M1 = self.timeseries.ta.atr(atr_length) * atr_mult
        sd = dwmas.rolling(window = sdlen).std()

        atrl = dwmas + M1
        atrs = dwmas - M1

        sdl = (dwmas + sd) * 1.035
        sds = (dwmas - sd) * 1.02
        xf = (sdl + sds) / 2

        long_condition = atrl if self.condition =="ATR" else sdl
        short_condition = atrs if self.condition == "ATR" else sds

        # Long and Short Conditions
        self.timeseries['Long'] = ( self.timeseries["close"] > long_condition).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < short_condition).astype(int)

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