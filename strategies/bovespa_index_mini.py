class CandleStick:
    def __init__(self, open_price, high_price, low_price, close_price):
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price

class MiniIndiceBovespa:
    def __init__(self):
        self.candles = []
        self.current_trade = None
        self.take_profit_price = None
        self.stop_loss_price = None

    def add_candle(self, candle):
        self.candles.append(candle)

    def get_previous_candles(self, count):
        return self.candles[-count:]

    def identify_candle_properties(self, candle):
        print(f"Open: {candle.open}, High: {candle.high}, Low: {candle.low}, Close: {candle.close}")

    def open_trade(self, entry_price, take_profit, stop_loss):
        self.current_trade = entry_price
        self.take_profit_price = entry_price + take_profit
        self.stop_loss_price = entry_price - stop_loss

    def close_trade(self):
        self.current_trade = None
        self.take_profit_price = None
        self.stop_loss_price = None
        print("Trade closed.")

    def check_take_profit(self, current_price):
        if self.current_trade is not None and current_price >= self.take_profit_price:
            print("Take profit reached. Closing trade.")
            self.close_trade()

    def check_stop_loss(self, current_price):
        if self.current_trade is not None and current_price <= self.stop_loss_price:
            print("Stop loss reached. Closing trade.")
            self.close_trade()

# # Example usage
# bot = MiniIndiceBovespa()

# # Add candles
# bot.add_candle(CandleStick(100, 110, 90, 105))
# bot.add_candle(CandleStick(105, 115, 100, 110))
# bot.add_candle(CandleStick(110, 120, 105, 115))

# # Get previous candles
# previous_candles = bot.get_previous_candles(2)
# for candle in previous_candles:
#     bot.identify_candle_properties(candle)

# # Open a trade
# bot.open_trade(110, take_profit=10, stop_loss=5)

# # Check take profit and stop loss
# bot.check_take_profit(120)  # Trade should close
# bot.check_stop_loss(105)   # Trade already closed, no effect