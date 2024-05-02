class BaseTradingStrategy:
    def __init__(self, lookback_period):
        self.lookback_period = lookback_period
        self.position = None

    def generate_signal(self, lookback_data):
        raise NotImplementedError("Method `generate_signal()` must be implemented in the child strategy class")

    def calculate_entry(self, signal, positions, close_price):
        raise NotImplementedError("Method `calculate_entry()` must be implemented in the child strategy class")

    def calculate_exit(self, signal, close_price, entry_price):
        raise NotImplementedError("Method `calculate_exit()` must be implemented in the child strategy class")
