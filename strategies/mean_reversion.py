import time

import numpy as np
import pandas as pd


def calculate_z_score(data):
    mean = data.mean()
    std_dev = data.std(ddof=0)
    z_score = (data.iloc[-1] - mean) / std_dev
    return z_score  # return the last element

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

class MeanReversionStrategy:
    def __init__(self, symbol, lookback_period, entry_threshold, exit_threshold, lot_size, poll_interval=None):
        self.poll_interval = poll_interval
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.lot_size = lot_size
        self.position = None

    def generate_signal(self, data):
        if 'Close' in data.columns or 'close' in data.columns:
            close_label = 'Close' if 'Close' in data.columns else 'close'
        else:
            raise KeyError("DataFrame nao contem uma coluna 'Close' ou 'close' como referencia ao preço de fechamento")

        z_score = calculate_z_score(data[close_label])
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
            print(f"Erro ao executar o sinal: {e}")

