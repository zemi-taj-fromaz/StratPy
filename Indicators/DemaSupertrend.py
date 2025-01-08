import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
class DemaSupertrend:
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
        for supLen in range(1, 9):
            for supMul in [x * 0.1 for x in range(23, 38, 1)]:  # Step by 0.1
                for demalen in range(5, 15):
                    equity = self.calculate( supLen, supMul, demalen)
                    print(equity)
                    self.store_result(equity, supLen, supMul, demalen)

        # Print top results
        top_results = self.get_top_results()
        print("Top Results:")
        for result in top_results:
            print(f"Equity: {result[0]}, DEMA Length: {result[1]}, Lookback: {result[2]}, Long: {result[3]}")


    def calculate(self,  supLen, supMul, demalen):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")
        self.strategy = cobra.Strategy(self.timeseries, self.startYear)
        self.timeseries['hlc3'] = (self.timeseries['high'] + self.timeseries['low'] + self.timeseries['close']) / 3

        # Calculate DEMA
        self.timeseries['DEMA'] = ta.dema(self.timeseries['hlc3'], length=demalen)
        self.timeseries["ATR"] = self.timeseries.ta.atr(length = supLen)

        # Initialize Supertrend Bands
        self.timeseries['UpperBand'] = self.timeseries['DEMA'] + supMul * self.timeseries['ATR']
        self.timeseries['LowerBand'] = self.timeseries['DEMA'] - supMul * self.timeseries['ATR']

        # Initialize shifted bands for persistence logic
        self.timeseries['PrevUpperBand'] = self.timeseries['UpperBand'].shift(1).fillna(0)
        self.timeseries['PrevLowerBand'] = self.timeseries['LowerBand'].shift(1).fillna(0)

        # Persist Upper and Lower Bands
        self.timeseries['UpperBand'] = self.timeseries.apply(
            lambda row: row['UpperBand'] if row['UpperBand'] < row['PrevUpperBand'] or row['close'] > row[
                'PrevUpperBand']
            else row['PrevUpperBand'], axis=1
        )

        self.timeseries['LowerBand'] = self.timeseries.apply(
            lambda row: row['LowerBand'] if row['LowerBand'] > row['PrevLowerBand'] or row['close'] < row[
                'PrevLowerBand']
            else row['PrevLowerBand'], axis=1
        )

        # Determine Supertrend direction and value
        self.timeseries['Direction'] = 1  # Start with a default value
        self.timeseries['Supertrend'] = self.timeseries['UpperBand']


        for i in range(1, len(self.timeseries)):
            if self.timeseries['close'].iloc[i - 1] > self.timeseries['PrevUpperBand'].iloc[i]:
                self.timeseries.at[i, 'Direction'] = -1
            elif self.timeseries['close'].iloc[i - 1] < self.timeseries['PrevLowerBand'].iloc[i]:
                self.timeseries.at[i, 'Direction'] = 1

            self.timeseries.at[i, 'Supertrend'] = (
                self.timeseries['LowerBand'].iloc[i] if self.timeseries['Direction'].iloc[i] == 1
                else self.timeseries['UpperBand'].iloc[i]
            )

        # Define Long and Short conditions
        self.timeseries['Long'] = self.timeseries['Direction'] == 1
        self.timeseries['Short'] = self.timeseries['Direction'] == -1


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