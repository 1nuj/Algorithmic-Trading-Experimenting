#WHAT IT DOES
#Buys SPY, sets take profit at 10% above and stop loss at 5% below. once hit, buys it again and continues until time frame complete

# region imports
from AlgorithmImports import *
# endregion

class CreativeAsparagusMonkey(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2023, 1, 1)
        self.SetEndDate(2024, 1, 1)
        self.SetCash(100000)

        spy = self.AddEquity("SPY", Resolution.Daily)
        #self.AddFuture, AddForex .. for others
        #Resolution.Minute, change time frame through this

        self.spy = spy.Symbol

        self.SetBenchmark("SPY")
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)
        #margin allows leverage, cash does not

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time

    def OnData(self, data):
        # Ensure the data for the symbol exists and is not None
        if self.spy not in data or data[self.spy] is None:
            return

        price = data[self.spy].Close

        if not self.Portfolio.Invested:
            if self.nextEntryTime <= self.Time:
                self.SetHoldings(self.spy, 1)  # Buy SPY with 100% of portfolio
                self.Log("Buy SPY @" + str(price))
                self.entryPrice = price  # Save the entry price

        elif self.entryPrice * 1.1 < price:  # Take profit at 10% above entry price
            self.Liquidate()  # Sell SPY
            self.Log("SELL SPY (Take Profit) @" + str(price))
            self.nextEntryTime = self.Time + self.period  # Wait for 31 days

        elif self.entryPrice * 0.95 > price:  # Stop loss at 5% below entry price
            self.Liquidate()  # Sell SPY
            self.Log("SELL SPY (Stop Loss) @" + str(price))
            self.nextEntryTime = self.Time + self.period  # Wait for 31 days

