import pandas as pd
import pandas_ta as ta
import time

import Indicators.DemaATR as datr
import Indicators.STC as stc
import Indicators.INDI7525 as seven
import Indicators.DemaRSIOverlay as demaRsi
import Indicators.LSMA as lsma
import Indicators.LSMAATR as lsmaatr
import Indicators.NormalizedKAMA as kama
import Indicators.MedianSD as msd
import Indicators.DemaSD as dsd
import Indicators.TSAlma as ts
import Indicators.SmoothLSMATrend as bikelife
import Indicators.HighestLowestTrend as hlt
import Indicators.KalmanRSI as krs
import Indicators.CasperSupertrend as cstd
import Indicators.RMAJordo as jordo # 83 - 1.07 11 1.45
import Indicators.EMAJordo as jordoema

df = pd.DataFrame() # Empty DataFrame

# Load data
df = pd.read_csv("timeseries/INDEX_SUIUSD_1D.csv", sep = ",")[["time", "open", "high", "low", "close"]]

#STC NEEDS TO BE REwORKED
#indi = seven.INDI7525(df)
#indi = lsma.LSMA(df)
#indi = msd.MedianSD(df)
#indi = ts.TSAlma(df)
#indi = dsd.DemaSD(df)
#indi = hlt.HLTrend(df)
#indi = krs.KalmanRSI(df)
#indi = cstd.CasperSupertrend(df)
##indi = jordoema.EMA(df) -> Ovo ponovi, nisam siguran ni da je skroz dobro uopce
#indi = datr.DemaATR(df)
#indi = demaRsi.DemaRSIOverlay(df)
#indi = lsmaatr.LSMAATR(df)
#KAMU mozda najbolje preskocit

start_time = time.time()  # Record the start time
#indi.run_test()
end_time = time.time()    # Record the end time
execution_time = end_time - start_time  # Calculate the duration
hours, remainder = divmod(execution_time, 3600)  # Convert to hours and remaining seconds
minutes, seconds = divmod(remainder, 60)

print(f"Execution time: {int(hours):02d}::{int(minutes):02d}::{seconds:05.2f}")



