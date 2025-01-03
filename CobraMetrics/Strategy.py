import math
import numpy as np

class Trade:
    def __init__(self, state, entry_equity, entry_price):
        self.state = state
        self.entry_equity = entry_equity
        self.peak_equity = entry_equity
        self.through_equity = entry_equity
        self.entry_price = entry_price
        self.max_dd = 0.0
        self.exit_price = 0.0

    def process(self, equity):
        if(equity > self.peak_equity):
            self.peak_equity = equity
            self.through_equity = equity
            return

        if(equity < self.through_equity):
            self.through_equity = equity
            self.max_dd = max(self.max_dd, round(100*(1 - self.through_equity / self.peak_equity), 2))


class Strategy:
    def __init__(self, timeseries, startYear):
        self.equity = 1
        self.timeseries = timeseries
        self.returns_array = []
        self.negative_returns_array = []
        self.positive_returns_array = []
        self.state = "neutral"
        self.entries = []
        self.startYear = startYear
        ################COBRA METRICS#################
        self.maxEquity = 1
        self.maxEquityDd = 0.0
        self.maxIntraTradeDD = 0.0
        self.trades = 1.0
        self.wintrades = 0.0
        self.gross_profit = 0.0
        self.gross_loss = 0.0
        self.profit_factor = 0
        self.profitable_percent = 0.0
        self.curent_trade = Trade(self.state, 1, 0)
        self.positive_area = 0.0
        self.negative_area = 0.0

        self.sharpe = 0.0
        self.sortino = 0.0
        self.omega = 0.0

    def computeMetrics(self):
        mean = np.average(self.returns_array)
        std = np.std(self.returns_array)
        neg_ret_std = np.std(self.negative_returns_array)
        if(std != 0.0):
            self.sharpe = mean / std * math.sqrt(365)
        if(neg_ret_std != 0):
            self.sortino = mean / neg_ret_std * math.sqrt(365)
        if(self.negative_area != 0):
            self.omega = self.positive_area / -self.negative_area

    def entry(self, new_state, index):
        #startYear condition
        if (self.state == new_state):
            return

        if( self.timeseries["time"][index] <= "2018-01-01"):
        #    print("ENTER " + new_state + " on " + self.timeseries["time"][index])
            self.state = new_state
            self.curent_trade = Trade(self.state, self.equity, self.timeseries["close"][index])
            return



        #print("STRATEGY FLIPPED " + new_state + " ON: " + self.timeseries["time"][index] + "Trade No: " + str(self.trades) + "Equity: " + str(self.equity))

      #  self.trades += 1
       # if(self.equity >= self.curent_trade.entry_equity):
       #     self.wintrades += 1
       #     self.gross_profit += self.equity - self.curent_trade.entry_equity
       # else:
       #     self.gross_loss +=  self.curent_trade.entry_equity - self.equity

        #self.profitable_percent = round(self.wintrades / (self.trades - 1) * 100, 2)
        #if(self.gross_loss != 0.0):
        #    self.profit_factor = round(self.gross_profit / self.gross_loss, 2)
        self.state = new_state
        #self.maxIntraTradeDD = max(self.maxIntraTradeDD, self.curent_trade.max_dd)
        self.curent_trade = Trade(new_state, self.equity, self.timeseries["close"][index])


    def process(self, index: int):
        #startYear condition
        if( self.timeseries["time"][index] <= "2018-01-02" or self.timeseries["time"][index] >= "2024-12-22"):
            return

        if(self.state == "neutral"):
            return

        dailyReturn = 0

        if(self.state == "long"):
            dailyReturn = self.timeseries["close"][index] / self.timeseries["open"][index] - 1
            self.equity *= (1 + dailyReturn)
        elif(self.state == "short"): ##FIX THIS (entry_price - current_price) / entry_price
            perpReturn = (self.curent_trade.entry_price - self.timeseries["close"][index]) / self.curent_trade.entry_price
            dailyReturn = 1 - self.timeseries["close"][index] / self.timeseries["open"][index]
            self.equity = (self.curent_trade.entry_equity * ( 1+ perpReturn))


        self.curent_trade.process(self.equity)

       # self.returns_array.append(dailyReturn)
       # if(dailyReturn < 0.0):
       #     self.negative_returns_array.append(dailyReturn)
      #      self.negative_area += dailyReturn
      #  else:
      #      self.positive_returns_array.append(dailyReturn)
      #      self.positive_area += dailyReturn

     #   self.maxEquity = max(self.maxEquity, self.equity)
     #   self.maxEquityDd = min(self.maxEquityDd, self.equity / self.maxEquity - 1)

        #mean = np.average(self.returns_array)
        #std = np.std(self.returns_array)
        #neg_ret_std = np.std(self.negative_returns_array)
        #if(std != 0.0):
        #    self.sharpe = mean / std * math.sqrt(365)
        #if(neg_ret_std != 0):
        #    self.sortino = mean / neg_ret_std * math.sqrt(365)
        #if(self.negative_area != 0):
        #    self.omega = self.positive_area / -self.negative_area

    def printMetrics(self):
        print("Equity Max DD: " + str(round(self.maxEquityDd*-100,2)) + "%")
        print("Intra-trade MaxDD: " + str(self.maxIntraTradeDD)+ "%")
        print("Sortino Ratio: " + str(self.sortino))
        print("Sharpe Ratio: " + str(self.sharpe))
        print("Profit Factor: " + str(self.profit_factor))
        print("Profitable %: " + str(self.profitable_percent))
        print("Trades: " + str(self.trades ))
        print("Omega Ratio: " + str(self.omega))
        print("Equity : " + str(self.equity))

