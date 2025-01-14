import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math




### OVO CE MORAT PRICEKAT VOLUME DATA


class EnhancedLNLTrend:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []

    def store_result(self,equity,dmilen, atrlen, emabase, trendL):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,dmilen, atrlen, emabase, trendL))
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
        for dmilen in range(1, 15):
            for atrlen in range(12, 30):
                for emabase in range(12, 30):
                    for trendL in range(7, 21):
                        equity = self.calculate(dmilen, atrlen, emabase, trendL)
                        print(equity)
                        self.store_result(equity,dmilen, atrlen, emabase, trendL)
        self.print_top_results()





    def calculate(self, dmilen, atrlen, emabase, trendL):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        bullishDMI = np.where(
            ((self.timeseries["high"] - self.timeseries["high"].shift(1)) > (self.timeseries["low"].shift(1) - self.timeseries["low"])) &
            ((self.timeseries["high"] - self.timeseries["high"].shift(1)) > 0),
            (self.timeseries["high"] - self.timeseries["high"].shift(1)),
            0
        )

        bearishDMI = np.where(
            ((self.timeseries["low"].shift(1) - self.timeseries["low"]) > (
                        self.timeseries["high"] - self.timeseries["high"].shift(1))) &
            ((self.timeseries["low"].shift(1) - self.timeseries["low"]) > 0),
            (self.timeseries["low"].shift(1) - self.timeseries["low"]),
            0
        )

        DMIup = 100 * bullishDMI.ta.rma(dmilen) / bullishDMI.ta.tr(True).ta.rma(dmilen)
        DMIdown = 100 * bearishDMI.ta.rma(dmilen) / bearishDMI.ta.tr(True).ta.rma(dmilen)

        ADXx = np.where(
            (DMIup + DMIdown) > 0,
            100 * np.abs(DMIup - DMIdown) / (DMIup + DMIdown),
            np.nan  # Assign NaN if the condition is not met
        )
        ADX = ADXx.ta.rma(dmilen)

        LNL_DMI = np.where(
            (DMIup > DMIdown) & (ADX > 20),  # First condition
            1,  # Assign 1 if the first condition is met
            np.where(
                (DMIup < DMIdown) & (ADX > 20),  # Second condition
                -1,  # Assign -1 if the second condition is met
                0  # Assign 0 otherwise
            )
        )




        gaussian_smooth = self.timeseries["close"].rolling(window=length).apply(gaussian_filter, raw=False, kwargs={'sigma':sigma})
        filtered_sma = ta.ema(gaussian_smooth, length)

        atr = self.timeseries.ta.atr(atr_length)

        # Long and Short Conditions
        self.timeseries['Long'] = ( self.timeseries["close"] > filtered_sma + atr * mult).astype(int)
        self.timeseries['Short'] = (self.timeseries["close"] < filtered_sma - atr * mult).astype(int)

        for i in range(max( length, atr_length), len(self.timeseries)):
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