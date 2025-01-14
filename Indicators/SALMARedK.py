import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class SalmaRedK:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length, smooth, mult, sdlen):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length, smooth, mult, sdlen))
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
        for length in range(12, 44):
            for smooth in range(19, 58):
                for mult in [x * 0.01 for x in range(55, 95, 2)]:  # Step by 0.1
                    for sdlen in range(19, 58):
                        equity = self.calculate(  length, smooth, mult, sdlen)
                        print(equity)
                        self.store_result(equity,  length, smooth, mult, sdlen)

        self.print_top_results()

    def calculate(self,length, smooth, mult, sdlen) :
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        baseline = self.timeseries["close"].ta.wma(sdlen)
        dev = mult * self.timeseries["close"].rolling(window=sdlen).std()
        upper = baseline + dev
        lower = baseline - dev

        cprice = np.where(
            self.timeseries["close"] > upper,
            upper,
            np.where(
                self.timeseries["close"] < lower,
                lower,
                self.timeseries["close"]
            )
        )

        REMA = cprice.ta.wma(length).ta.wma(smooth)


        self.timeseries['Long'] = (REMA > REMA.shift(1)).astype(int)
        self.timeseries['Short'] = (REMA <= REMA.shift(1)).astype(int)



        for i in range(max(length, sdlen), len(self.timeseries['close'])):
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