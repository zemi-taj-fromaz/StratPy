import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class HmaSD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, demaLength, sd_length, sd_mult):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  demaLength, sd_length, sd_mult))
        if len(self.top_results) > 10:
            heapq.heappop(self.top_results)


    def get_top_results(self):
        return sorted(self.top_results, key=lambda x: -x[0])

    def run_test(self):
        """
        Run the optimization test over the parameter ranges and store the results.
        """
        for demaLength in range(7, 16):
            for sd_length in range(9, 22):
                for sd_mult in [x * 0.1 for x in range(14, 25, 1)]:  # Step by 0.1
                    equity = self.calculate( demaLength, sd_length, sd_mult)
                    print(equity)
                    self.store_result(equity,  demaLength, sd_length, sd_mult)

        # Print top results
        top_results = self.get_top_results()
        print("Top Results:")
        for result in top_results:
            params = [f"Equity: {result[0]}"] + [f"Param-{i + 1}: {param}" for i, param in enumerate(result[1:])]
            params.append(f"Trades: {self.strategy.trades}")  # Adding trade count
            print(", ".join(params))


    def calculate(self,  demaLength, sd_length, sd_mult):
        print(f"Calculating for: dema_length={demaLength}, rsi_length={sd_length}, long_threshold={sd_mult}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate DEMA
        hma = ta.hma(self.timeseries['close'], length=demaLength)

        # Calculate RSI of DEMA
        self.timeseries['deviation'] = self.timeseries["close"] - hma
        self.timeseries['STDEV'] = self.timeseries['deviation'].rolling(window=sd_length).std()

        # Calculate Volatility Bands
        self.timeseries['D'] = hma - self.timeseries['STDEV'] * sd_mult
        self.timeseries['U'] = hma + self.timeseries['STDEV'] * sd_mult

        # Long and Short Conditions
        self.timeseries['Long'] = (self.timeseries['close'] > self.timeseries['U'])
        self.timeseries['Short'] = (self.timeseries['close'] < self.timeseries['D'])


        for i in range(len(self.timeseries['Long'])):
                self.strategy.process(i)
                if (self.timeseries['Long'][i]):
                    self.strategy.entry("long", i)
                    continue
                if(self.timeseries['Short'][i]):
                    self.strategy.entry("short", i)
                    continue



     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series