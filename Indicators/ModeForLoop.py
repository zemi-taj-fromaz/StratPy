import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq

def system(x_, a ,b):
    start =  x_.index.start
    stop = x_.index.stop
    # Apply Gaussian weights
    sum = 0
    for i in range(a, b + 1):
        sum += 1 if (x_[stop - 1] > x_[stop - 1 - i]) else -1

    return sum

def rolling_mode(series):
    """
    This function calculates the mode of a pandas Series.
    It returns the most frequent value or NaN if the mode is empty.
    """
    mode_val = series.mode()
    return mode_val.iloc[0] if not mode_val.empty else np.nan

class MedianForLoop:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity, length, a, b):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, length, a, b))
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
        for length in range(2, 22):
            for a in range(1, 13):
                for b in range(a+40, 62):
                    equity = self.calculate( length, a, b)
                    print(equity)
                    self.store_result(equity,  length, a, b)

        self.print_top_results()


    def calculate(self,  length, a, b):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        subject = self.timeseries["close"].rolling(window=length).apply(rolling_mode, raw = False)
        score = subject.rolling(window = b + 1).apply(system, raw=False, kwargs={'a':a, 'b':b})

       # Long and Short Conditions
        self.timeseries['Long'] = (score > 40).astype(int)
        self.timeseries['Short'] = (score < -10).astype(int)

        for i in range(b + 1, len(self.timeseries['close'])):
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