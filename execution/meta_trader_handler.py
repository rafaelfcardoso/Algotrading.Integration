import MetaTrader5 as mt5
import pandas as pd

from datetime import datetime
import time


class MetaTraderExecutionHandler:
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

    def check_take_profit(self, position_id, symbol, take_profit_price, volume):
        """
        Checks if the current price has reached the desired take profit price. If so, closes the operation.

        Args:
            position_id (int): The position ticket number.
            symbol (str): The ticker symbol of the instrument.
            take_profit_price (float): The desired take profit price.
            volume (float): The volume of the order (e.g., 1 lot of a future mini-contract)

        Returns:
            bool: True if the position was closed successfully due to hitting the take profit, False otherwise.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Erro: Falha ao conectar ao terminal MetaTrader 5.")
                return False

        current_price = mt5.symbol_info_tick(symbol).last

        if (volume > 0 and current_price >= take_profit_price) or (volume < 0 and current_price <= take_profit_price):
            print(f"Preço de Take Profit alcançado para {symbol}.")
            return self.close_position(position_id, symbol, volume)

        return False

    def market_buy_order(self, symbol, volume, deviation=20):
        """
        Places an order in the MetaTrader 5 terminal.

        Args:
            symbol (str): The ticker symbol of the instrument.
            action (int): The action of the order (e.g., mt5.ORDER_BUY, mt5.ORDER_SELL).
            volume (float): The volume of the order (e.g., 1 lot of a future mini-contract)
            order_type (int): The type of the order (e.g., mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL).
            deviation (int): The deviation in points from the current price.

        Returns:
            int: The order ticket number.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Erro: Falha ao conectar ao terminal MetaTrader 5.")
                return None
        
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask #if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - 100 * point,
            "tp": price + 100 * point,
            "deviation": deviation,
            "magic": 234000,
            "comment": "Python script open trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        result = mt5.order_send(request)
        print(f"Ordem enviada: {volume} lote de {symbol} ao preco de {price} com desvio de {deviation} pontos")

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Envio da ordem falhou, retcode={result.retcode}, comment={result.comment}")
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            return None

        return result.order
    
    def market_sell_order(self, symbol, volume, deviation=20):
        """
        Places an order in the MetaTrader 5 terminal.

        Args:
            symbol (str): The ticker symbol of the instrument.
            action (int): The action of the order (e.g., mt5.ORDER_BUY, mt5.ORDER_SELL).
            volume (float): The volume of the order (e.g., 1 lot of a future mini-contract)
            order_type (int): The type of the order (e.g., mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL).
            deviation (int): The deviation in points from the current price.

        Returns:
            int: The order ticket number.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Erro: Falha ao conectar ao terminal MetaTrader 5.")
                return None
        
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": price + 100 * point,
            "tp": price - 100 * point,
            "deviation": deviation,
            "magic": 234000,
            "comment": "Python script open trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN
        }

        result = mt5.order_send(request)

        print(f"Ordem enviada a mercado: -{volume} lotes de {symbol} ao preco de {price} com desvio de {deviation} pontos")
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Envio da ordem falhou, retcode={result.retcode}, comment={result.comment}")
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            return None
        
        return True
    
    def close_position(self, position_id, symbol, volume: float):
        """
        Closes an open position in the MetaTrader 5 terminal.

        Args:
            position_id (int): The position ticket number.
            symbol (str): The ticker symbol of the instrument.
            volume (float): The volume of the order (e.g., 1 lot of a future mini-contract)

        Returns:
            bool: True if the position was closed successfully, False otherwise.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Erro: Falha ao conectar ao terminal MetaTrader 5.")
                return False
            
        price = mt5.symbol_info_tick(symbol).bid
        deviation = 20
        position_closed = False

        if volume > 0.0:
            print("Fechando posicao #{}: venda de {} lotes de {} no preco {}".format(
                position_id, volume, symbol, price, deviation))
            position_closed = self.market_sell_order(symbol, volume)

        elif volume < 0.0:
            print("Fechando posicao #{}: compra de {} lotes de {} no preco {}".format(
                position_id, volume, symbol, price, deviation))
            position_closed = self.market_buy_order(symbol, volume)

        if position_closed is False:
            print("Erro ao fechar posicao #{}".format(position_id))
            return False
        
        elif position_closed is True:
            print("Posicao #{} fechada com sucesso.".format(position_id))
            return True
