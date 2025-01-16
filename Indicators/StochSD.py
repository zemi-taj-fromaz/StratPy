import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq



#### MMMM PRESKOCI OVO NESOT JEBE SA NONE VRIJEDNOSTIMA



class StochSD:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, length, sdlength):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,length, sdlength))
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
        for length in range(12, 40):
            for sdlength in range(20, 50):
                equity = self.calculate(length, sdlength)
                print(equity)
                self.store_result(equity,length, sdlength)

        self.print_top_results()

    # Define a helper function to safely handle None and float arithmetic
    def safe_add(self, a, b):
        return None if a is None or b is None else a + b

    def safe_sub(self, a, b):
        return None if a is None or b is None else a - b
    def calculate(self,  length, sdlength):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        stoch = self.timeseries.ta.stoch(length)
        print(stoch)
        atr = ta.stdev(stoch, sdlength)

        # Compute upper and lower bands using the helper functions
        upper = stoch.apply(lambda x: self.safe_add(x, atr) if atr is not None else None)
        lower = stoch.apply(lambda x: self.safe_sub(x, atr) if atr is not None else None)

        # Long and Short Conditions
        self.timeseries['Long'] = (lower > 50).astype(int)
        self.timeseries['Short'] = (stoch < 50).astype(int)



        for i in range(max( length, sdlength), len(self.timeseries)):
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