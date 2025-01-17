import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

def system(x_):
    start =  x_.index.start
    stop = x_.index.stop

    N = stop - start

    x = np.zeros(N)
    y = np.zeros(N)
    #######################
    xArr = np.zeros(N)
    yArr = np.zeros(N)
    for i in range(N):
        x[i] = x_[stop - 1 -i]

    # Perform DFT
    for i in range(N):
        xArr_i = 0.0
        yArr_i = 0.0
        kx = float(i) / float(N)
        _arg = -2 * math.pi * kx

        for k in range(N):
            _cos = math.cos(k * _arg)
            _sin = math.sin(k * _arg)
            xArr_i += x[k] * _cos - y[k] * _sin
            yArr_i += x[k] * _sin + y[k] * _cos
        xArr[i] = xArr_i
        yArr[i] = yArr_i
    # #####################
    x[:] = xArr / N
    y[:] = yArr / N

    return np.sqrt(x[0] ** 2 + y[0] ** 2)

def forloop(x_, start):
    begin =  x_.index.start
    stop = x_.index.stop

    return_val = 0

    for i in range(begin,  stop - start):
        return_val += 1 if x_[stop - 1] > x_[i] else -1
    # #####################
    return return_val

class DMIForLoop:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self, equity,N, start, end, upper, lower):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity, N, start, end, upper, lower))
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
        for N in range(1, 6):
            for start in range(1, 5):
                for end in range(40, 50):
                    for upper in range(end - start - 10, end - start):
                        for lower in range(start - end + 30, upper - 11):
                            equity = self.calculate( N, start, end, upper, lower)
                            print(equity)
                            self.store_result(equity, N, start, end, upper, lower)

        self.print_top_results()


    def calculate(self, a, b, c):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        up = self.timeseries['high'].diff()
        down = -self.timeseries["low"].diff()

        self.timeseries['plusDM'] = np.where(
            (self.timeseries['up'] > self.timeseries['down']) & (self.timeseries['up'] > 0),
            self.timeseries['up'],
            0
        )

        self.timeseries['minusDM'] = np.where(
            (self.timeseries['down'] > self.timeseries['up']) & (self.timeseries['down'] > 0),
            self.timeseries['down'],
            0
        )

        xval = (self.timeseries["close"] + self.timeseries["high"] + self.timeseries["low"]) / 3

        subject = xval.rolling(window = N).apply(system)

        score = subject.rolling(window = end + 1).apply(forloop, raw=False, kwargs={'start':start})

       # Long and Short Conditions
        self.timeseries['Long'] = (score > upper).astype(int)
        self.timeseries['Short'] = (score < lower).astype(int)

        for i in range(end + 1, len(self.timeseries['close'])):
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