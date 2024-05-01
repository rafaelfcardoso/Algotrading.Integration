import numpy as np
import pandas as pd


def calculate_z_score(data):
    mean = data.mean()
    std_dev = data.std(ddof=0)
    z_score = (data.iloc[-1] - mean) / std_dev
    return z_score  # return the last element


class MeanReversionStrategy:
    def __init__(self, symbol, lookback_period, entry_threshold, exit_threshold, lot_size):
        self.symbol = symbol
        self.lookback_period = lookback_period
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.lot_size = lot_size
        self.position = None

    def generate_signal(self, data):
        z_score = calculate_z_score(data['Close'])
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

    def calculate_profit(self, entry_price, exit_price, position):
        return position * (exit_price - entry_price) * self.lot_size

    # def backtest(self, data):
    #     signals = [0] * len(data)
    #     positions = [0] * len(data)
    #     profits = [0] * len(data)
    #     entry_price = None
    #
    #     for i in range(self.lookback_period, len(data)):
    #         lookback_data = data[i - self.lookback_period:i]
    #         signal = self.generate_signal(lookback_data)
    #
    #         if signal is not None:
    #             current_close = lookback_data['Close'].iloc[-1]
    #
    #             if signal == 'BUY':
    #                 positions[i] = 1
    #                 entry_price = current_close
    #             elif signal == 'SELL':
    #                 positions[i] = -1
    #                 entry_price = current_close
    #             elif signal == 'CLOSE' and entry_price is not None:
    #                 position = positions[-1]
    #
    #                 profit = self.calculate_profit(entry_price, current_close, position)
    #                 profits[i] = profit
    #                 entry_price = None
    #         else:
    #             if i > 0:
    #                 positions[i] = positions[i - 1]
    #                 profits[i] = profits[i - 1]
    #
    #     return pd.DataFrame({'Signal': signals, 'Position': positions, 'Profit': profits},
    #                         index=data.index)

    # def backtest(self, data): # Second solution
    #     signals = []
    #     positions = []
    #     profits = []
    #     entry_price = None
    #
    #     for i in range(self.lookback_period, len(data)):
    #         lookback_data = data[i - self.lookback_period:i]
    #         signal = self.generate_signal(lookback_data)
    #
    #         if signal is not None:
    #             current_close = lookback_data['Close'].iloc[-1]
    #
    #             if signal == 'BUY':
    #                 positions.append(1)
    #                 entry_price = current_close
    #
    #             elif signal == 'SELL':
    #                 positions.append(-1)
    #                 entry_price = current_close
    #
    #             elif signal == 'CLOSE' and entry_price is not None:
    #                 position = positions[-1]
    #                 profit = self.calculate_profit(entry_price, current_close, position)
    #                 profits.append(profit)
    #                 entry_price = None
    #
    #                 signals.append(signal)
    #
    #             else:
    #                 signals.append(None)
    #
    #         # If signal is None, repeat the previous values (or write 0 if there are no previous values)
    #         else:
    #             signals.append(None if len(signals) == 0 else signals[-1])
    #             positions.append(0 if len(positions) == 0 else positions[-1])
    #             profits.append(0 if len(profits) == 0 else profits[-1])
    #
    #     # Now signals, positions, and profits lists are the same size as the data from data.index
    #     result_df = pd.DataFrame({'Signal': signals, 'Position': positions, 'Profit': profits},
    #                              index=data.index[self.lookback_period:])
    #
    #     return result_df

    # def backtest(self, data): #ORIGINAL backtest
    #     signals = []
    #     positions = []
    #
    #     for i in range(self.lookback_period, len(data)):
    #         lookback_data = data[i - self.lookback_period:i]
    #         signal = self.generate_signal(lookback_data)
    #         entry_price = None
    #         position = None
    #
    #         if signal is not None:
    #             signals.append(signal)
    #             if signal == 'BUY':
    #                 positions.append(1)
    #             elif signal == 'SELL':
    #                 positions.append(-1)
    #             else:
    #                 positions.append(0)
    #         else:
    #             signals.append(None)
    #             positions.append(positions[-1] if len(positions) > 0 else 0)
    #     return pd.DataFrame({'Signal': signals, 'Position': positions}, index=data.index[self.lookback_period:])

    # OPUS SOLUTION

    def backtest(self, data):
        signals = []
        positions = []
        profits = [None] * len(data)  # Initialize profits with None values
        entry_price = None
        total_profit = 0

        for i in range(self.lookback_period, len(data)):
            lookback_data = data[i - self.lookback_period:i]
            signal = self.generate_signal(lookback_data)
            close_price = data['Close'][i]

            if signal is not None:
                signals.append(signal)
                if signal == 'BUY':
                    if positions[-1] != 'LONG':
                        entry_price = close_price
                elif signal == 'SELL':
                    if positions[-1] != 'SHORT':
                        entry_price = close_price
                elif signal == 'CLOSE' and self.position is None:
                    profit = self.calculate_profit(entry_price, close_price,
                                                   1 if self.position == 'LONG' else -1)
                    profits[i] = profit  # Update profits at the current index
                    total_profit += profit

            else:
                signals.append(None)

            positions.append(self.position)

        if self.position is not None:
            close_price = data['Close'][-1]
            profit = self.calculate_profit(entry_price, close_price, 1 if self.position == 'LONG' else -1)
            profits[-1] = profit  # Update profits at the last index
            total_profit += profit

        return pd.DataFrame({'Signal': signals, 'Position': positions, 'Profit': profits[self.lookback_period:]},
                            index=data.index[self.lookback_period:]), total_profit
