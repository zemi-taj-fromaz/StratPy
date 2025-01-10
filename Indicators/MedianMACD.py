import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class MedianMACD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, fastLength, slowlength, MACDLength, MedLookBack):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,fastLength, slowlength, MACDLength, MedLookBack))
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
        for fastLength in range(35, 85):
            for slowlength in range(1, 17):
                for MACDLength in range(35, 85):
                    for MedLookBack in range(1, 17):
                        equity = self.calculate(fastLength, slowlength, MACDLength, MedLookBack)
                        print(equity)
                        self.store_result(equity,fastLength, slowlength, MACDLength, MedLookBack)

        self.print_top_results()

    def calculate(self,  fastLength, slowlength, MACDLength, MedLookBack):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        self.timeseries['median'] = self.timeseries["close"].rolling(window=MedLookBack).quantile(0.5)
        self.timeseries['MACD'] = ta.ema(self.timeseries["median"], fastLength) -  ta.ema(self.timeseries["median"], slowlength)
        self.timeseries["aMACD"] = ta.ema( self.timeseries['MACD'] ,MACDLength )

        delta =  self.timeseries['MACD'] - self.timeseries["aMACD"]



        # Long and Short Conditions
        self.timeseries['Long'] = (delta > 0).astype(int)
        self.timeseries['Short'] = (delta < 0).astype(int)



        for i in range(max(slowlength, fastLength, MACDLength, MedLookBack), len(self.timeseries)):
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