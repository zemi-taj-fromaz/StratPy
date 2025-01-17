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
import Indicators.RMAJordo as jordo # 83 - 1.07 11 1.45 ## OVO JE U KURCU, NE VALJA NES, TAKO DA MOLIM TE POPRAVI KAD CE TI SE DAT
import Indicators.EMAJordo as jordoema
import Indicators.ISDDemaRSI as vii
import Indicators.DemaSupertrend as dst
import Indicators.DoubleSrcSMASD as dssmasd
import Indicators.DemaSMASD as demasmasd
import Indicators.ViiStop
import Indicators.ViiStop as vst
import Indicators.EWMA
import Indicators.DemaEmaCross
import Indicators.DemaDMI
import Indicators.DSMA
import Indicators.EWMAOsc
import Indicators.NormT3Osc
import Indicators.NeutralStateStochOsc
import Indicators.PPSarOsc
import Indicators.MomentumZenithGuide
import Indicators.FourMACD
import Indicators.DynamicMedianEMA
import Indicators.AlmaLag
import Indicators.MedianSupertrend
import Indicators.NeutralStateBollingerBands
import Indicators.NeutralStateMACD
import Indicators.RsiSD
import Indicators.DemaAFR
import Indicators.HullForLoopRocheur
import Indicators.EnhancedKijunSenBase
import Indicators.MacdEmaSd
import Indicators.GEMAD
import Indicators.JordoRSIZScore
import Indicators.ZlsmaSupertrend
import Indicators.EnhancedHMA5DSD
import Indicators.MedianMACD
import Indicators.StochSD
import Indicators.EmaSD
import Indicators.EnhancedKeltnerTrend
import Indicators.PDFSmoothedMA
import Indicators.SALMARedK
import Indicators.DemaAFR
import Indicators.EmaZScore
import Indicators.BBMultiplier
import Indicators.VawDema
import Indicators.VawDemaCross
import Indicators.FourierForLoop
import Indicators.KalmanFilteredRSIOscillator
import Indicators.KalmanHullRsiOscillator
import Indicators.PPSarOsc

df = pd.DataFrame() # Empty DataFrame

# Load data
df = pd.read_csv("timeseries/ETHUSD_1D.csv", sep = ",")[["time", "open", "high", "low", "close", "volume"]]

#### OSCILATORS #####

#indi = Indicators.EWMAOsc.EwmaOsc(df)
#indi = Indicators.KalmanFilteredRSIOscillator.KalmanPriceFilter(df)
#indi = Indicators.NormT3Osc.NormT3Osc(df)
#indi = Indicators.KalmanHullRsiOscillator.KalmanHullRsiOscillator(df) #### EHHHH THIS KIND OF SUCKS; no need to program this though
#indi = Indicators.NeutralStateStochOsc.NSSTC(df)
#indi = Indicators.PPSarOsc.PPSarOsc(df) # SMECE NE GUBI VRIJEME
indi = Indicators.MomentumZenithGuide.Zenith(df) # NAZALOST SMECE IZGLEDA DA JE DOSTA ZAJEBANO I SPORO _> IAKO MAYBE U BUDUCNOSTI
indi = stc.STC(df)

#### PERPETUALS #####

#indi = seven.INDI7525(df)
#indi = lsma.LSMA(df)
#indi = msd.MedianSD(df)
#indi = ts.TSAlma(df)
#indi = dsd.DemaSD(df)
#indi = hlt.HLTrend(df)
#indi = krs.KalmanRSI(df)
#indi = Indicators.MacdEmaSd.MacdEmaSd(df)
#indi = cstd.CasperSupertrend(df)
##indi = jordoema.EMA(df) -> Ovo ponovi, nisam siguran ni da je skroz dobro uopce
#indi = datr.DemaATR(df)
#indi = inid.dynamicMedianEma.DynamicMedianEma(df)
#indi = inid.dynamicMedianEma.DynamicMedianEma(df, sd)
#indi = demaRsi.DemaRSIOverlay(df)
#indi = lsmaatr.LSMAATR(df)
#KAMU mozda najbolje preskocit
#indi = vii.ISDDemaRSI(df)
#indi = Indicators.AlmaLag.AlmaLag(df)
#indi = dst.DemaSupertrend(df)
#indi = dssmasd.DoubleSrcSMASD(df)
#indi = demasmasd.DemaSMASD(df)
#indi = Indicators.ViiStop.ViiStop(df)
#indi = Indicators.EWMA.Ewma(df)
#indi = Indicators.MedianSupertrend.MedianSupertrend(df)
#indi = Indicators.DSMA.dsma(df)

#indi = Indicators.Indicators.FourMACD.Zenith(df) #VOLUME DATA NOT AVAIL - useless _TODO TOMOOROWO
#indi = Indicators.FourMACD useless as fuck nazalost
#indi = Indicators.DemaEmaCross.DemaEmaCross(df)
#indi = Indicators.DemaDMI.DemaDMI(df)
#indi = Indicators.DemaSupertrend.DemaSupertrend(df)
#indi = Indicators.NeutralStateBollingerBands.NSBB(df)
#indi = Indicators.NeutralStateMACD.NSMacD(df)
#indi = Indicators.RsiSD.RsiSD(df)
#indi = Indicators.DemaAFR.DemaAFR(df)
#indi = Indicators.HullForLoopRocheur.HullForLoop(df)
#indi = Indicators.EnhancedKijunSenBase.EnhancedKijunSenBase(df)
#indi = Indicators.GEMAD.GEMAD(df) ### OVAJ MALLO PRESPORO TRAJE:; DUGO SE TESTIRAM
#indi = Indicators.JordoRSIZScore.RSIZScore(df)
#indi = Indicators.ZlsmaSupertrend.ZlsmaSupertrend(df)
#indi = jordo.RMA(df)
#indi = Indicators.EnhancedHMA5DSD.EnhancedRicky(df)
#indi = Indicators.MedianMACD.MedianMACD(df)
#indi = Indicators.StochSD.StochSD(df) -> Slobodno preskoci ovaj, jebe sa None type errorima
#indi = bikelife.SmoothLSMATrend(df)
#indi = Indicators.EmaSD.EmaSD(df)
#indi = Indicators.EnhancedKeltnerTrend.EnhancedKeltnerTrend(df)
#indi = Indicators.PDFSmoothedMA.PDFSmoothedMA(df)
#indi = Indicators.SALMARedK.SalmaRedK(df) ### OVAJ MALLO PRESPORO TRAJE:; DUGO SE TESTIRAM
#indi = Indicators.DemaAFR.DemaAFR(df)
#indi = Indicators.EmaZScore.EmaZScore(df)
#indi = Indicators.BBMultiplier.BBMultiplier(df) ### SOMETHING IS FUCKED WITH THIS DONT USEs
#indi = Indicators.VawDema.VawDema(df)
#indi = Indicators.VawDemaCross.VawDemaCross(df)
#indi = Indicators.FourierForLoop.FFL(df)



start_time = time.time()  # Record the start time
indi.run_test()
end_time = time.time()    # Record the end time
execution_time = end_time - start_time  # Calculate the duration
hours, remainder = divmod(execution_time, 3600)  # Convert to hours and remaining seconds
minutes, seconds = divmod(remainder, 60)

print(f"Execution time: {int(hours):02d}::{int(minutes):02d}::{seconds:05.2f}")



