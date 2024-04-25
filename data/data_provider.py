from abc import ABC, abstractmethod
import pandas as pd
import yfinance as yf
import MetaTrader5 as mt5

from datetime import datetime
import time


class DataProviderBase(ABC):
    @abstractmethod
    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        pass

    @abstractmethod
    def get_realtime_data(self, symbol):
        pass


class YahooFinanceDataProvider(DataProviderBase):
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
        
class AlphaVantageDataProvider(DataProviderBase):
    def __init__(self, api_key):
        self.api_key = api_key
        self.ts = TimeSeries(key=api_key)

    def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
        try:
            data, _ = self.ts.get_daily_adjusted(symbol, outputsize='full')
            data = pd.DataFrame(data).T
            data.index = pd.to_datetime(data.index)
            data = data.loc[start_date:end_date]
            return data
        except Exception as e:
            print(f"Error retrieving historical data from Alpha Vantage for {symbol}: {str(e)}")
            return None

    def get_realtime_data(self, symbol):
        try:
            data, _ = self.ts.get_quote_endpoint(symbol)
            return float(data['05. price'])
        except Exception as e:
            print(f"Error retrieving real-time data from Alpha Vantage for {symbol}: {str(e)}")
            return None

class MetaTraderDataProvider(DataProviderBase):
    def __init__(self):
        self.connected = False

    def connect(self):
        """
        Connects to the MetaTrader 5 terminal.

        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        if not self.connected:
            self.connected = mt5.initialize()
            return self.connected
        return True

    def disconnect(self):
        """
        Disconnects from the MetaTrader 5 terminal.
        """
        if self.connected:
            mt5.shutdown()
            self.connected = False

    def get_historical_data(self, symbol, start_date, end_date, timeframe):
        """
        Retrieves historical price data for a given symbol and date range.

        Args:
            symbol (str): The ticker symbol of the instrument.
            start_date (str): The start date of the historical data (YYYY-MM-DD).
            end_date (str): The end date of the historical data (YYYY-MM-DD).
            timeframe (int): The timeframe of the historical data (e.g., mt5.TIMEFRAME_M1, mt5.TIMEFRAME_H1).

        Returns:
            pd.DataFrame: A DataFrame containing the historical price data.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected to MetaTrader 5 terminal.")
            return None

        try:
            data = mt5.copy_rates_range(symbol, timeframe, datetime.strptime(start_date, "%Y-%m-%d"), datetime.strptime(end_date, "%Y-%m-%d"))
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            return df
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {str(e)}")
            return None
        
    def get_ohlc(self, symbol, timeframe, n = 5):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2500)
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected to MetaTrader 5 terminal.")
                return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        return df


    def get_realtime_data(self, symbol):
        """
        Retrieves real-time price data for a given symbol.

        Args:
            symbol (str): The ticker symbol of the instrument.

        Returns:
            float: The current price of the instrument.
        """
        if not self.connected:
            print("Error: Not connected to MetaTrader 5 terminal.")
            return None

        try:
            rates = mt5.symbol_info_tick(symbol)
            #print(f"{symbol} - last: {rates.last}, bid: {rates.bid}, ask: {rates.ask}")
            return rates.bid
        except Exception as e:
            print(f"Error retrieving real-time data for {symbol}: {str(e)}")
            return None

    def place_order(self, symbol, action, volume, order_type, price):
        """
        Places an order in the MetaTrader 5 terminal.

        Args:
            symbol (str): The ticker symbol of the instrument.
            action (int): The action of the order (e.g., mt5.ORDER_BUY, mt5.ORDER_SELL).
            volume (float): The volume of the order.
            order_type (int): The type of the order (e.g., mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL).
            price (float): The price of the order.

        Returns:
            int: The order ticket number.
        """
        if not self.connected:
            print("Error: Not connected to MetaTrader 5 terminal.")
            return None

        request = {
            "action": action,
            "symbol": symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC
        }

        result = mt5.order_send(request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Error placing order: {result.comment}")
            return None

        return result.order


def data_provider_factory(provider_name, api_key=None):
    if provider_name == 'yahoo':
        return YahooFinanceDataProvider()
    elif provider_name == 'meta_trader':
        return MetaTraderDataProvider()
    elif provider_name == 'alpha_vantage':
        return AlphaVantageDataProvider(api_key)
    else:
        raise ValueError(f"Unsupported data provider: {provider_name}")
    
# Usage example
config = {
    'data_provider': 'meta_trader',
    'api_key': None
}

# data_provider = data_provider_factory(config['data_provider'], config['api_key'])
# historical_data = data_provider.get_historical_data('AAPL', '2022-01-01', '2022-12-31')
# ohlc_data = data_provider.get_ohlc('WIN$', mt5.TIMEFRAME_M1, 5)
# realtime_price = data_provider.get_realtime_data('AAPL')