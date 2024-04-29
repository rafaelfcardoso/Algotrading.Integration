import pandas as pd


class MeanReversionBacktester:
    def __init__(self, strategy):
        self.strategy = strategy

    def run(self, data):
        try:
            signals = []
            positions = []
            for i in range(self.strategy.lookback_period, len(data)):
                lookback_data = data[i - self.strategy.lookback_period:i]
                signal = self.strategy.generate_signal(lookback_data)
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
            return pd.DataFrame({'Signal': signals, 'Position': positions},
                                index=data.index[self.strategy.lookback_period:])
        except Exception as e:
            print(f"Error during backtesting: {e}")
            return None
