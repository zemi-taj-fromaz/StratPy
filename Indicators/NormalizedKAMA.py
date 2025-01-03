import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class NormalizedKAMA:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, fast_period, slow_period, er_period, norm_period):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,fast_period, slow_period, er_period, norm_period))
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
        for fast_period in range(3, 12):
            for slow_period in range(14, 25):
                for er_period in range(4, 14):
                    for norm_period in range(40, 50, 2):
                        equity = self.calculate( fast_period, slow_period, er_period, norm_period)
                        print(equity)
                        self.store_result(equity, fast_period, slow_period, er_period, norm_period)

        self.print_top_results()

    def calculate(self, fast_period, slow_period, er_period, norm_period):
        print(f"Calculating KAMA with fast_period={fast_period}, slow_period={slow_period}, "
              f"er_period={er_period}, norm_period={norm_period}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        change = abs(self.timeseries['close'] - self.timeseries['close'].shift(er_period))
        volatility = self.timeseries['close'].diff().abs().rolling(window=er_period).sum()
        er = change / volatility
        sc = er * (2 / (fast_period + 1) - 2 / (slow_period + 1)) + 2 / (slow_period + 1)

        ema_fast = self.timeseries.ta.ema(length=fast_period)
        kama = ema_fast + sc* ( self.timeseries['close'] - ema_fast)

        # Apply normalization based on norm_period
        kama_max = kama.rolling(window=norm_period).max()
        kama_min = kama.rolling(window=norm_period).min()
        kama_normalized = (kama - kama_min) / (kama_max - kama_min) - 0.5

        self.timeseries['Long'] = kama_normalized > 0
        self.timeseries['Short'] = kama_normalized < 0


        for i in range(norm_period, len(self.timeseries['close'])):
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