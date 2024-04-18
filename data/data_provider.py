import pandas as pd
import yfinance as yf

class DataProvider:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        """
        Retrieves historical price data for a given symbol and date range.

        Args:
            symbol (str): The ticker symbol of the instrument.
            start_date (str): The start date of the historical data (YYYY-MM-DD).
            end_date (str): The end date of the historical data (YYYY-MM-DD).
            interval (str): The interval of the historical data (e.g., '1d', '1h', '1m').

        Returns:
            pd.DataFrame: A DataFrame containing the historical price data.
        """
        try:
            data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
            return data
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {str(e)}")
            return None

    def get_realtime_data(self, symbol):
        """
        Retrieves real-time price data for a given symbol.

        Args:
            symbol (str): The ticker symbol of the instrument.

        Returns:
            float: The current price of the instrument.
        """
        try:
            data = yf.download(symbol, period='1d', interval='1m')
            return data['Close'][-1]
        except Exception as e:
            print(f"Error retrieving real-time data for {symbol}: {str(e)}")
            return None