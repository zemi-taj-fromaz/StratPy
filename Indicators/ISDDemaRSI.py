import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class ISDDemaRSI:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,  sublen, sublen_2, lenx, Threshold_L, Threshold_S):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  sublen, sublen_2, lenx, Threshold_L, Threshold_S))
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
        for sublen in range(26, 33):
            for sublen_2 in range(25, 32):
                for lenx in range(10, 18):
                    for Threshold_L in range(60, 80):  # Step by 0.1
                        for Threshold_S in range(40, 70):  # Step by 0.1
                            equity = self.calculate(sublen, sublen_2, lenx, Threshold_L, Threshold_S)
                            print(equity)
                            self.store_result(equity, sublen, sublen_2, lenx, Threshold_L, Threshold_S)

        self.print_top_results()

    def calculate(self,  sublen, sublen_2, lenx, Threshold_L, Threshold_S):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries["dema"] = self.timeseries.ta.dema(length=sublen)
        self.timeseries["rsi"] = ta.rsi(self.timeseries["dema"], length=lenx)
        self.timeseries["stdev"] = self.timeseries["dema"].rolling(window = sublen_2).std()
        # Calculate the highest high over l_length periods and multiply by l_multi
        # Calculate Volatility Bands
        self.timeseries['U'] = self.timeseries['dema'] + self.timeseries['stdev']
        self.timeseries['D'] = self.timeseries['dema'] - self.timeseries['stdev']
        # Support Levels
        #  self.timeseries['SUPL'] = self.timeseries['close'] > self.timeseries['D']
        self.timeseries['SUPS'] = self.timeseries['close'] < self.timeseries['U']

        # Long and Short Conditions
        self.timeseries['Long'] = (self.timeseries['rsi'] > Threshold_L) & (~self.timeseries['SUPS'])
        self.timeseries['Short'] = (self.timeseries['rsi'] < Threshold_S)



        for i in range(max(sublen,sublen_2), len(self.timeseries)):
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