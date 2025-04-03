from AlgorithmImports import *

class MovingAverageCrossoverAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2024, 1, 1)  # Set start date
        self.SetEndDate(2025,1,1)
        self.SetCash(100000)  # Set initial capital
        
        self.symbol = self.AddEquity("NVDA", Resolution.Daily).Symbol  # Use SPY (S&P 500 ETF)
        
        # Define moving averages
        self.fast_ma = self.SMA(self.symbol, 10, Resolution.Daily)
        self.slow_ma = self.SMA(self.symbol, 50, Resolution.Daily)
        
        self.previous_cross = None  # To track crossover events
        self.entry_price = None  # Track entry price for SL/TP
        self.stop_loss_pct = 0.05  # 5% stop-loss
        self.take_profit_pct = 0.10  # 10% take-profit
    
    def OnData(self, data):
        if not self.fast_ma.IsReady or not self.slow_ma.IsReady:
            return  # Wait until indicators are ready
        
        fast_value = self.fast_ma.Current.Value
        slow_value = self.slow_ma.Current.Value
        current_price = self.Securities[self.symbol].Price
        
        # Check if stop-loss or take-profit conditions are met
        if self.entry_price:
            stop_loss_price = self.entry_price * (1 - self.stop_loss_pct)
            take_profit_price = self.entry_price * (1 + self.take_profit_pct)
            
            if current_price <= stop_loss_price or current_price >= take_profit_price:
                self.Liquidate(self.symbol)  # Exit trade
                self.entry_price = None  # Reset entry price
                return
        
        # Buy signal: fast MA crosses above slow MA
        if fast_value > slow_value and (self.previous_cross is None or self.previous_cross == "bearish"):
            self.SetHoldings(self.symbol, 1)  # Invest fully in SPY
            self.previous_cross = "bullish"
            self.entry_price = current_price  # Store entry price for SL/TP
        
        # Sell signal: fast MA crosses below slow MA
        elif fast_value < slow_value and (self.previous_cross is None or self.previous_cross == "bullish"):
            self.Liquidate(self.symbol)  # Sell all holdings
            self.previous_cross = "bearish"
            self.entry_price = None  # Reset entry price