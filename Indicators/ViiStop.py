import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import pandas as pd
class ViiStop:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity, lenx, mul):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,  lenx, mul))
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
        for lenx in range(2, 22):
            for mul in [x * 0.1 for x in range(18, 37, 1)]:  # Step by 0.1
                equity = self.calculate( lenx, mul)
                print(equity)
                self.store_result(equity, lenx, mul)

        self.print_top_results()

    def calculate(self,   lenx, mul):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)
        self.timeseries['atr'] = self.timeseries.ta.atr(length=lenx)

        # Initialize variables for Vii' Stop logic
        uptrend = True
        self.timeseries['Max'] = self.timeseries['close']
        self.timeseries['Min'] = self.timeseries['close']
        self.timeseries['Stop'] = None

        atrM = self.timeseries['atr'] * mul



        for i in range(lenx, len(self.timeseries)):
                self.strategy.process(i)
                # Get previous stop value (shifted for comparison)
                prev_stop = self.timeseries['Stop'].loc[i - 1] if not pd.isna(self.timeseries['Stop'].loc[i - 1]) else self.timeseries['close'].loc[i]

                # Update max and min
                self.timeseries.loc[i, 'Max'] = max(self.timeseries['Max'].loc[i - 1],
                                                     self.timeseries['close'].loc[i])
                self.timeseries.loc[i, 'Min'] = min(self.timeseries['Min'].loc[i - 1],
                                                     self.timeseries['close'].loc[i])

                # Calculate stop value
                stop = prev_stop
                if uptrend:
                    stop = max(stop, self.timeseries['Max'].loc[i] - atrM.loc[i])
                else:
                    stop = min(stop, self.timeseries['Min'].loc[i] + atrM.loc[i])

                # Set stop value
                self.timeseries.loc[i, 'Stop'] = stop

                # Determine uptrend direction
                uptrend = self.timeseries['close'].loc[i] - stop >= 0.0

                if(self.timeseries['close'][i] < stop):
                    self.strategy.entry("short", i)
                    continue

                if(self.timeseries['close'][i] >= stop):
                    self.strategy.entry("long", i)
                    continue


     #   self.strategy.printMetrics()
        return self.strategy.equity

        # Simplified example: double the value of each item in the series