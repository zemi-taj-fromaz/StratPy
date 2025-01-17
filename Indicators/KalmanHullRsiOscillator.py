import pandas_ta as ta
import matplotlib.pyplot as plt
import numpy as np
import CobraMetrics.Strategy as cobra
import heapq
import math

from numba import njit


def f_kalman(x_, stateEstimate, errorCovariance, measurementNoise, processNoise):
    start =  x_.index.start
    stop = x_.index.stop

    length = stop - start

    predictedStateEstimate = np.copy(stateEstimate)
    predictedErrorCovariance = errorCovariance + processNoise

    kalmanGain = predictedErrorCovariance / (predictedErrorCovariance + measurementNoise)

    for i in range(length):

        # Update state estimate
        stateEstimate[i] = (
                predictedStateEstimate[i] + kalmanGain[i] * (x_[stop - 1] - predictedStateEstimate[i])
        )

        # Update error covariance
        errorCovariance[i] = (1 - kalmanGain[i]) * predictedErrorCovariance[i]

    return stateEstimate[0]

class KalmanHullRsiOscillator:
    def __init__(self, timeseries, startYear = "2018"):
        self.timeseries = timeseries
        self.startYear = startYear
        self.strategy = cobra.Strategy(self.timeseries, startYear)
        self.top_results = []
        self.stateEstimate = np.zeros(1)  # Reinitialize stateEstimate to match the size of N
        self.errorCovariance = np.zeros(1)  # Empty NumPy array
    def store_result(self,equity, processNoise, measurementNoise, N, rsiPeriod):
        """
        Store the result in the heap, keeping only the top 10 results.
        """
        heapq.heappush(self.top_results, (equity,processNoise, measurementNoise, N, rsiPeriod))
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
        N = 5
        processNoise = 0.01
        self.stateEstimate = np.zeros(N)   # Update with values from timeseries
        self.stateEstimate[:] = self.timeseries["close"][0]
        self.errorCovariance = np.zeros(N)   # Update with values from timeseries
        self.errorCovariance[:] = 100.0  # Update all elements to 1.0
        for measurementNoise in range(1, 12):  # Step by 0.1
            for rsiPeriod in range(2, 27, 1):
                equity = self.calculate(processNoise, measurementNoise, N, rsiPeriod)
                print(equity)
                self.store_result(equity,processNoise, measurementNoise, N, rsiPeriod)
        self.print_top_results()

    def calculate(self,  processNoise, measurementNoise, N, rsiPeriod):
        args = locals()  # returns a dictionary of all local variables
        print(f"Calculating for: {', '.join(f'{key}={value}' for key, value in args.items() if key != 'self')}")

        self.strategy = cobra.Strategy(self.timeseries, self.startYear)

        kalmanFilteredPrice = self.timeseries["close"].rolling(window=N).apply(f_kalman, raw=False, kwargs={'stateEstimate':self.stateEstimate, "errorCovariance":self.errorCovariance,
                                                                                                        'measurementNoise' : measurementNoise, 'processNoise':processNoise})
        kkfp = self.timeseries["close"].rolling(window=N).apply(f_kalman, raw=False, kwargs={'stateEstimate':self.stateEstimate, "errorCovariance":self.errorCovariance,
                                                                                                        'measurementNoise' : measurementNoise, 'processNoise':processNoise})
        half_kkfp = self.timeseries["close"].rolling(window=N).apply(f_kalman, raw=False, kwargs={'stateEstimate':self.stateEstimate, "errorCovariance":self.errorCovariance,
                                                                                                        'measurementNoise' : measurementNoise / 2, 'processNoise':processNoise})
        hma = 2 * half_kkfp - kkfp
        hkma = hma.rolling(window=N).apply(f_kalman, raw=False, kwargs={'stateEstimate':self.stateEstimate, "errorCovariance":self.errorCovariance,
                                                                                                        'measurementNoise' : round(math.sqrt(measurementNoise)) , 'processNoise':processNoise})

        rsi = ta.rsi(hkma, rsiPeriod)

        self.timeseries['Long'] = (rsi > 50).astype(int)
        self.timeseries['Short'] = (rsi < 50).astype(int)

        for i in range(max(N, rsiPeriod), len(self.timeseries)):
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