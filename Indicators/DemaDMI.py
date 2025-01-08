import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd















## NESTO JEBE LIBRARY: NE KORISTI














class DemaDMI:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, demalen, adxlen, dmilen):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,   demalen, adxlen, dmilen))
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
        for demalen in range(15, 32):
            for adxlen in range(12, 28):
                for dmilen in range(12, 28):
                    equity = self.calculate(  demalen, adxlen, dmilen)
                    print(equity)
                    self.store_result(equity,  demalen, adxlen, dmilen)

        self.print_top_results()

    def calculate(self,    demalen, adxlen, dmilen):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)
        self.timeseries['demah'] = self.timeseries.ta.dema(source = "high", length=demalen)
        self.timeseries['demal'] = self.timeseries.ta.dema(source = "low", length=demalen)

        u = self.timeseries["demah"] - self.timeseries["demah"].shift(1)
        d = self.timeseries["demal"].shift(1) - self.timeseries["demal"]

        # Calculate True Range (TR) manually
        self.timeseries['high_close_prev'] = self.timeseries['high'].shift(1)
        self.timeseries['low_close_prev'] = self.timeseries['low'].shift(1)
        self.timeseries['close_prev'] = self.timeseries['close'].shift(1)

        self.timeseries['tr'] = np.maximum(self.timeseries['high'] - self.timeseries['low'],
                                           np.abs(self.timeseries['high'] - self.timeseries['close_prev']),
                                           np.abs(self.timeseries['low'] - self.timeseries['close_prev']))

        p = np.where(u > d, np.where(u > 0, u, 0), 0)
        m = np.where(d > u, np.where(d > 0, d, 0), 0)

        # True range and smoothing of ADX
        t = ta.rma(self.timeseries["tr"], dmilen)
        plus = 100 * np.nan_to_num( ta.rma(p, dmilen) ) / t
        minus = 100 * np.nan_to_num( ta.rma(m, dmilen) ) / t
        sum_ = plus + minus
        adx = 100 * ta.rma(np.abs(plus - minus) / np.where(sum_ == 0, 1, sum_), adxlen)

        # Determine trend direction based on ADX
        x = adx > adx.shift(1)
        dmil = (plus > minus) & x
        dmis = (minus > plus)

        self.timeseries['Long'] = (self.timeseries['ema1'] > self.timeseries['ema2']).astype(int)
        self.timeseries['Short'] = (self.timeseries['ema1'] < self.timeseries['ema2']).astype(int)

        for i in range(max(demalen, adxlen, dmilen), len(self.timeseries)):
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