import numpy as np
import pandas as pd

class MeanReversionStrategy:
    def __init__(self, symbol, lookback_period, entry_threshold, exit_threshold, lot_size):
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.lot_size = lot_size
        self.position = None

    def calculate_z_score(self, data):
        mean = np.mean(data)
        std_dev = np.std(data)
        z_score = (data[-1] - mean) / std_dev
        return z_score

    def generate_signal(self, data):
        z_score = self.calculate_z_score(data)
        if z_score < -self.entry_threshold and self.position != 'LONG':
            self.position = 'LONG'
            return 'BUY'
        elif z_score > self.entry_threshold and self.position != 'SHORT':
            self.position = 'SHORT'
            return 'SELL'
        elif self.position == 'LONG' and z_score > -self.exit_threshold:
            self.position = None
            return 'CLOSE'
        elif self.position == 'SHORT' and z_score < self.exit_threshold:
            self.position = None
            return 'CLOSE'
        else:
            return None

    def execute_signal(self, signal, execution_handler):
        try:
            if signal == 'BUY':
                execution_handler.market_buy_order(self.symbol, self.lot_size)
            elif signal == 'SELL':
                execution_handler.market_sell_order(self.symbol, self.lot_size)
            elif signal == 'CLOSE':
                if self.position == 'LONG':
                    execution_handler.close_position(self.position, self.symbol, -self.lot_size)
                elif self.position == 'SHORT':
                    execution_handler.close_position(self.position, self.symbol, self.lot_size)
        except Exception as e:
            print(f"Error executing signal: {e}")

    def backtest(self, data):
        try:
            signals = []
            positions = []
            for i in range(self.lookback_period, len(data)):
                lookback_data = data[i - self.lookback_period:i]
                signal = self.generate_signal(lookback_data)
                if signal is not None:
                    signals.append(signal)
                    if signal == 'BUY':
                        positions.append(1)
                    elif signal == 'SELL':
                        positions.append(-1)
                    else:
                        positions.append(0)
                else:
                    signals.append(None)
                    positions.append(positions[-1] if len(positions) > 0 else 0)
            return pd.DataFrame({'Signal': signals, 'Position': positions}, index=data.index[self.lookback_period:])
        except Exception as e:
            print(f"Error during backtesting: {e}")
            return None