import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class MedianSD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, median_len, atr_len, atr_mul, sd_len):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,median_len, atr_len, atr_mul, sd_len))
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
        for median_len in range(55, 65):
            for atr_len in range(6, 15):
                for atr_mul in [x * 0.1 for x in range(1, 6, 1)]:  # Step by 0.1
                    for sd_len in range(18, 27):
                        equity = self.calculate( median_len, atr_len, atr_mul, sd_len)
                        print(equity)
                        self.store_result(equity,  median_len, atr_len, atr_mul, sd_len)

        self.print_top_results()

    def calculate(self, median_len, atr_len, atr_mul, sd_len) :
        print(f"Calculating for: {median_len}, {atr_len}, {atr_mul} {sd_len}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries['median'] = self.timeseries["close"].rolling(window=median_len).quantile(0.5)
        self.timeseries['ATR'] = self.timeseries.ta.atr(length=atr_len) * atr_mul
        # Entry confirmation source

        self.timeseries['u'] =self.timeseries['median']+ self.timeseries['ATR']
        self.timeseries['l'] = self.timeseries['median'] - self.timeseries['ATR']

        self.timeseries['sd'] = self.timeseries["median"].rolling(window=sd_len).std()
        self.timeseries['sdd'] = self.timeseries['median'] + self.timeseries['sd']
        self.timeseries['sdl'] = self.timeseries['median'] - self.timeseries['sd']


        # Crossover and Crossunder Logic
        self.timeseries['Long'] = ((self.timeseries['close'] > self.timeseries['l']) & (
                    self.timeseries['close'] >= self.timeseries['sdd'])).astype(int)
        self.timeseries['Short'] = (self.timeseries['close'] < self.timeseries['u']).astype(int)



        for i in range(median_len, len(self.timeseries['close'])):
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