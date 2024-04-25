import MetaTrader5 as mt5
import pandas as pd


class RiskManagement():
    def __init__(self):
        pass
    
    def get_positions(self):
        """
        Retrieves the open positions in the MetaTrader 5 terminal.

        Returns:
            pd.DataFrame: A DataFrame containing the open positions.
        """

        if not mt5.initialize():
          print("initialize() failed, error code =",mt5.last_error())
          quit()

        positions = mt5.positions_get()
        if positions is not None:
            positions_data = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
            return positions_data
        return None