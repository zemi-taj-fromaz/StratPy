import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class DemaSMASD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, len_dema, len_ma, len_sd):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, len_dema, len_ma, len_sd))
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
        for len_dema in range(1, 10):
            for len_ma in range(40, 80):
                for len_sd in range(10, 35):
                    equity = self.calculate(len_dema, len_ma, len_sd)
                    print(equity)
                    self.store_result(equity,len_dema, len_ma, len_sd)

        self.print_top_results()

    def calculate(self,  len_dema, len_ma, len_sd):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)
        self.timeseries['hl2'] = (self.timeseries['high'] + self.timeseries['low']) / 2

        # Calculate the highest low over h_length periods and multiply by h_multi
        self.timeseries["dema"] = ta.dema(self.timeseries["hl2"], len_dema)
        self.timeseries["sma"] = ta.sma(self.timeseries["dema"],  len_ma)
        self.timeseries["sd"] = self.timeseries["sma"].rolling(window = len_sd).std()


        self.timeseries['u'] = self.timeseries['sma'] + self.timeseries['sd']
        self.timeseries['l'] = self.timeseries['sma'] - self.timeseries['sd']


        # Long and Short Conditions
        self.timeseries['Long'] = (self.timeseries['high'] >  self.timeseries['l'])
        self.timeseries['Short'] = (self.timeseries['low'] <  self.timeseries['u'])



        for i in range(len_ma, len(self.timeseries)):
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