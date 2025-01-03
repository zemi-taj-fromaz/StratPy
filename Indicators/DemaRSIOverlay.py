import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class DemaRSIOverlay:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, demaLength, rsi_length, long_threshold, short_threshold):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, demaLength, rsi_length, long_threshold, short_threshold))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)


    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def run_test(self):
        """
        Run the optimization test over the parameter ranges and store the results.
        """
        for demaLength in range(22, 37):
            for rsi_length in range(12, 18):
                for long_threshold in range(68, 72):
                    for short_threshold in range(53, 57):
                        equity = self.calculate(demaLength, rsi_length, long_threshold, short_threshold)
                        self.store_result(equity, demaLength, rsi_length, long_threshold, short_threshold)

        # Print top results
        top_results = self.get_top_results()
        print("Top Results:")
        for result in top_results:
            print(f"Equity: {result[0]}, DEMA Length: {result[1]}, Lookback: {result[2]}, Long: {result[3]}, Short: {result[4]}")


    def calculate(self, dema_length: int, rsi_length: int, long_threshold: float, short_threshold: float):
        print(f"Calculating for: dema_length={dema_length}, rsi_length={rsi_length}, long_threshold={long_threshold}, short_threshold={short_threshold}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate DEMA
        self.timeseries['DEMA'] = ta.dema(self.timeseries['close'], length=dema_length)

        # Calculate RSI of DEMA
        self.timeseries['RSI_DEMA'] = ta.rsi(self.timeseries['DEMA'], length=rsi_length)

        # Calculate standard deviation of DEMA
        self.timeseries['STDEV'] = self.timeseries['DEMA'].rolling(window=dema_length).std()

        # Calculate Volatility Bands
        self.timeseries['U'] = self.timeseries['DEMA'] + self.timeseries['STDEV']
        self.timeseries['D'] = self.timeseries['DEMA'] - self.timeseries['STDEV']


        # Support Levels
      #  self.timeseries['SUPL'] = self.timeseries['close'] > self.timeseries['D']
        self.timeseries['SUPS'] = self.timeseries['close'] < self.timeseries['U']

        # Long and Short Conditions
        self.timeseries['Long'] = (self.timeseries['RSI_DEMA'] > long_threshold) & (~self.timeseries['SUPS'])
        self.timeseries['Short'] = (self.timeseries['RSI_DEMA'] < short_threshold)


        for i in range(len(self.timeseries['Long'])):
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