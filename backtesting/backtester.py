import pandas as pd


class Backtester:
    def __init__(self, strategy, lot_size):
        self.strategy = strategy
        self.lot_size = lot_size

    def calculate_profit(self, entry_price, exit_price, position):
        return position * (exit_price - entry_price) * self.lot_size

    # def run_backtest(self, data, lookback_period):
    #     signals = []
    #     positions = []
    #     profits = []
    #
    #     for i in range(lookback_period, len(data)):
    #         lookback_data = data[i - lookback_period:i]
    #         signal = self.strategy.generate_signal(lookback_data)
    #         entry_price = None
    #         position = None
    #
    #         if signal is not None:
    #             current_close = lookback_data['Close'].iloc[-1]
    #
    #             signals.append(signal)
    #             if signal == 'BUY':
    #                 positions.append(1)
    #                 entry_price = current_close
    #             elif signal == 'SELL':
    #                 positions.append(-1)
    #                 entry_price = current_close
    #             elif signal == 'CLOSE' and entry_price is not None:
    #                 if position == 'LONG':
    #                     position = 1
    #                 elif position == 'SHORT':
    #                     position = -1
    #
    #                 profit = self.calculate_profit(entry_price, current_close, position)
    #                 profits.append(profit)
    #                 entry_price = None
    #         else:
    #             positions.append(0 if len(profits) == 0 else profits[-1])  # for cases where no action is taken
    #
    #     results = pd.DataFrame({'Signal': signals, 'Position': positions, 'Profit': profits}, index=data.index)
    #
    #     # Calculate total profit
    #     total_profit = results['Profit'].sum()
    #
    #     return results, total_profit

    def run_backtest(self, data, lookback_period):
        signals = [0] * len(data)
        positions = [0] * len(data)
        profits = [0] * len(data)
        entry_price = None

        for i in range(lookback_period, len(data)):
            lookback_data = data[i - lookback_period:i]
            signal = self.strategy.generate_signal(lookback_data)

            if signal is not None:
                current_close = lookback_data['Close'].iloc[-1]

                if signal == 'BUY':
                    positions[i] = 1
                    entry_price = current_close
                elif signal == 'SELL':
                    positions[i] = -1
                    entry_price = current_close
                elif signal == 'CLOSE' and entry_price is not None:
                    position = positions[-1]

                    profit = self.calculate_profit(entry_price, current_close, position)
                    profits[i] = profit
                    entry_price = None
            else:
                if i > 0:
                    positions[i] = positions[i - 1]
                    profits[i] = profits[i - 1]

        results = pd.DataFrame({'Signal': signals, 'Position': positions, 'Profit': profits}, index=data.index)

        # Calculate total profit
        total_profit = results['Profit'].sum()

        return results, total_profit

