import pandas as pd
from pytz import timezone
import yfinance as yf
import MetaTrader5 as mt5

from abc import ABC, abstractmethod
from datetime import datetime


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


# class AlphaVantageDataProvider(DataProviderBase):
#     def __init__(self, api_key):
#         self.api_key = api_key
#         self.ts = TimeSeries(key=api_key)
# 
#     def get_historical_data(self, symbol, start_date, end_date, interval='1d'):
#         try:
#             data, _ = self.ts.get_daily_adjusted(symbol, outputsize='full')
#             data = pd.DataFrame(data).T
#             data.index = pd.to_datetime(data.index)
#             data = data.loc[start_date:end_date]
#             return data
#         except Exception as e:
#             print(f"Error retrieving historical data from Alpha Vantage for {symbol}: {str(e)}")
#             return None
# 
#     def get_realtime_data(self, symbol):
#         try:
#             data, _ = self.ts.get_quote_endpoint(symbol)
#             return float(data['05. price'])
#         except Exception as e:
#             print(f"Error retrieving real-time data from Alpha Vantage for {symbol}: {str(e)}")
#             return None

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

    def get_ticks_from_start(self, symbol: str, start_date: str, end_date: str, flags=mt5.COPY_TICKS_ALL):
        """
        Retrieves ticks for a given symbol and date range.

        Args:
            symbol (str): The ticker symbol of the instrument.
            start_date (str): The start date of the data (YYYY-MM-DD).
            end_date (str): The end date of the data (YYYY-MM-DD).
            flags (int): Type of requested data (mt5.COPY_TICKS_ALL, mt5.COPY_TICKS_INFO).

        Returns:
            Array of CopyTicks* structures or None in case of failure.
        """
        if not mt5.terminal_info():
            print("Terminal is not connected, trying to connect...")
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected")
                return None

        ticks = mt5.copy_ticks_range(symbol, start_date, end_date, flags)

        if ticks is None:
            print('No ticks obtained')
            return ticks
        else:
            print('Ticks obtained', len(ticks))

        # create DataFrame out of the obtained data
        ticks_frame = pd.DataFrame(ticks)
        # convert time in seconds into the datetime format
        ticks_frame['time'] = pd.to_datetime(ticks_frame['time'], unit='s')

        # display data
        print("\nDisplay dataframe with ticks")
        print(ticks_frame.head(10))
        return ticks_frame

    def get_historical_data(self, symbol, start_date, end_date, interval=mt5.TIMEFRAME_M1):
        """
        Retrieves historical price data for a given symbol and date range.

        Args:
            symbol (str): The ticker symbol of the instrument.
            start_date (str): The start date of the historical data (YYYY-MM-DD).
            end_date (str): The end date of the historical data (YYYY-MM-DD).
            interval (int): The timeframe of the historical data (e.g., mt5.TIMEFRAME_M1, mt5.TIMEFRAME_H1).

        Returns:
            pd.DataFrame: A DataFrame containing the historical price data.
        """
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected to MetaTrader 5 terminal.")
                return None

        # create 'datetime' objects in UTC time zone to avoid the implementation of a local time zone offset
        try:
            data = mt5.copy_rates_range(symbol, interval, datetime.strptime(start_date, "%Y-%m-%d"),
                                        datetime.strptime(end_date, "%Y-%m-%d"))
            df = pd.DataFrame(data)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            return df
        except Exception as e:
            print(f"Error retrieving historical data for {symbol}: {str(e)}")
            return None

    def get_previous_candles(self, symbol, timeframe, count=5):
        """
                Fetches OHLC data for the previous N last candles.

                Args:
                    symbol (str): The ticker symbol of the instrument.
                    timeframe (int): The timeframe to retrieve data for (e.g., mt5.TIMEFRAME_M15 for 15-minute bars).
                    count (int) : The number of candles to retrieve.

                Returns
                    pandas.DataFrame: A DataFrame containing the OHLC data.
                """

        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2500)
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Erro: Falha ao conectar ao terminal MetaTrader 5.")
                return None

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        if rates is None:
            print("Erro: Não foi possível obter dados OHLC.")
            return None
        else:
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
            # print(f"{symbol} - last: {rates.last}, bid: {rates.bid}, ask: {rates.ask}")
            return rates
        except Exception as e:
            print(f"Error retrieving real-time data for {symbol}: {str(e)}")
            return None


def data_provider_factory(provider_name, api_key=None):
    if provider_name == 'yahoo':
        return YahooFinanceDataProvider()
    elif provider_name == 'metatrader':
        return MetaTraderDataProvider()
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
