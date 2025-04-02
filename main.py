#FIRST THIRTY ANALYSIS STRATEGY
from AlgorithmImports import *
from datetime import time  # Correctly importing the time class from datetime module

class CreativeAsparagusMonkey(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)

        spy = self.AddEquity("SPY", Resolution.Minute)  # Minute resolution for intra-day trading
        self.spy = spy.Symbol
        self.SetBenchmark("SPY")
        
        # Corrected market open time definition
        self.marketOpenTime = time(9, 30)  # Market opens at 9:30 AM EST
        self.sessionEndTime = time(10, 0)  # 30 minutes after market opens
        self.highPoint = None
        self.lowPoint = None

        # Variables to manage trades and exits
        self.entryPrice = 0
        self.position = None
        self.period = timedelta(31)
    
    def OnData(self, data):
        # Ensure the data for the symbol exists and is not None
        if self.spy not in data or data[self.spy] is None:
            return
        
        currentTime = self.Time.time()

        # First, capture the high and low during the first 30 minutes of the session
        if self.highPoint is None or self.lowPoint is None:  # Check if we've already captured high/low points
            if self.marketOpenTime <= currentTime <= self.sessionEndTime:
                price = data[self.spy].Close
                if self.highPoint is None or price > self.highPoint:
                    self.highPoint = price  # Update high point
                if self.lowPoint is None or price < self.lowPoint:
                    self.lowPoint = price  # Update low point

        # Once the 30-minute window is over, start trading based on high/low points
        if self.highPoint is not None and self.lowPoint is not None:
            # Check for shorting (price hits the low point)
            if self.Portfolio.Invested == False and data[self.spy].Close <= self.lowPoint:
                self.position = "short"
                self.entryPrice = data[self.spy].Close
                self.SetHoldings(self.spy, -1)  # Short SPY
                self.Log("Short SPY @" + str(self.entryPrice))

            # Check for longing (price hits the high point)
            elif self.Portfolio.Invested == False and data[self.spy].Close >= self.highPoint:
                self.position = "long"
                self.entryPrice = data[self.spy].Close
                self.SetHoldings(self.spy, 1)  # Long SPY
                self.Log("Long SPY @" + str(self.entryPrice))

            # Take Profit and Stop Loss for Long Position
            if self.position == "long" and data[self.spy].Close >= self.entryPrice * 1.1:  # 10% Take Profit
                self.Liquidate()  # Sell SPY
                self.Log("Take Profit Long SPY @" + str(data[self.spy].Close))
                self.position = None
                self.nextEntryTime = self.Time + self.period  # Wait 31 days

            elif self.position == "long" and data[self.spy].Close <= self.entryPrice * 0.95:  # 5% Stop Loss
                self.Liquidate()  # Sell SPY
                self.Log("Stop Loss Long SPY @" + str(data[self.spy].Close))
                self.position = None
                self.nextEntryTime = self.Time + self.period  # Wait 31 days

            # Take Profit and Stop Loss for Short Position
            if self.position == "short" and data[self.spy].Close <= self.entryPrice * 0.9:  # 10% Take Profit
                self.Liquidate()  # Buy to cover SPY
                self.Log("Take Profit Short SPY @" + str(data[self.spy].Close))
                self.position = None
                self.nextEntryTime = self.Time + self.period  # Wait 31 days

            elif self.position == "short" and data[self.spy].Close >= self.entryPrice * 1.05:  # 5% Stop Loss
                self.Liquidate()  # Buy to cover SPY
                self.Log("Stop Loss Short SPY @" + str(data[self.spy].Close))
                self.position = None
                self.nextEntryTime = self.Time + self.period  # Wait 31 days
