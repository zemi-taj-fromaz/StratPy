import pandas as pd
import pandas_ta as ta
import time

import Indicators.DemaATR as indi
import Indicators.STC as stc
import Indicators.INDI7525 as seven
import Indicators.DemaRSIOverlay as demaRsi
import Indicators.LSMA as lsma
import Indicators.LSMAATR as lsmaatr
import Indicators.NormalizedKAMA as kama

df = pd.DataFrame() # Empty DataFrame

# Load data
df = pd.read_csv("timeseries/INDEX_ETHUSD, 1D.csv", sep = ",")[["time", "open", "high", "low", "close"]]

#df["dema"] = df.ta.dema(length = 10)

#stc = stc.STC(df)
#stc.calculate(0.675, 10, 45, 175)
#indi7525 = seven.INDI7525(df)

#indi = lsma.LSMA(df)

indi = kama.NormalizedKAMA(df)

start_time = time.time()  # Record the start time
indi.run_test()
end_time = time.time()    # Record the end time
execution_time = end_time - start_time  # Calculate the duration
hours, remainder = divmod(execution_time, 3600)  # Convert to hours and remaining seconds
minutes, seconds = divmod(remainder, 60)

print(f"Execution time: {int(hours):02d}::{int(minutes):02d}::{seconds:05.2f}")



