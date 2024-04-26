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

        try:
            positions = mt5.positions_get()
            #print("Posicao de {} lotes de {} encontrada.".format(positions['volume'][0], positions['symbol'][0]))
            #print("Posicao de {} lotes de {} encontrada. Resultado atual de {}".format(positions['volume'][0], positions['symbol'][0], positions['profit'][0]))
            if len(positions) is not 0:
                positions_data = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())

            else:
                print("No positions found.")
                positions_data = None

            return positions_data
        
        except Exception as e:
            print(f"Error retrieving positions: {str(e)}")
            return None
