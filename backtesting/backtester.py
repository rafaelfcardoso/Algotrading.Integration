import pandas as pd


class Backtester:
    def __init__(self, strategy, lot_size):
        self.strategy = strategy
        self.lot_size = lot_size

    def calculate_profit(self, entry_price, exit_price, position):
        return position * (exit_price - entry_price) * self.lot_size

    def run(self, data):
        signals = []
        positions = []
        profits = [None] * len(data)  # Initialize profits with None values
        entry_price = None
        total_profit = 0

        if 'Close' in data.columns or 'close' in data.columns:
            close_label = 'Close' if 'Close' in data.columns else 'close'
        else:
            raise KeyError("DataFrame does not contain column 'Close' or 'close'")

        for i in range(self.strategy.lookback_period, len(data)):
            lookback_data = data[i - self.strategy.lookback_period:i]
            signal = self.strategy.generate_signal(lookback_data)
            close_price = data[close_label].iloc[i]

            if signal is not None:
                signals.append(signal)
                if signal == 'BUY':
                    if positions[-1] != 'LONG':
                        entry_price = close_price
                elif signal == 'SELL':
                    if positions[-1] != 'SHORT':
                        entry_price = close_price
                elif signal == 'CLOSE' and self.strategy.position is None:
                    profit = self.calculate_profit(entry_price, close_price,
                                                   1 if self.strategy.position == 'LONG' else -1)
                    profits[i] = profit  # Update profits at the current index
                    total_profit += profit

            else:
                signals.append(None)

            positions.append(self.strategy.position)

        if self.strategy.position is not None:
            close_price = data['Close'][-1]
            profit = self.calculate_profit(entry_price, close_price, 1 if self.strategy.position == 'LONG' else -1)
            profits[-1] = profit  # Update profits at the last index
            total_profit += profit

        result_df = pd.DataFrame({
            'Sinal': signals,
            'Posição': positions,
            'Lucro/Prejuízo': profits[self.strategy.lookback_period:]},
            index=data.index[self.strategy.lookback_period:]
        )

        result_df = result_df.fillna({'Lucro/Prejuízo': 0.00})
        total_profit_label = f"Resultado total: {total_profit}"
        return result_df, total_profit_label

