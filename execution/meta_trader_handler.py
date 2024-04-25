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

    def place_market_order(self, symbol, volume):
        """
        Places an order in the MetaTrader 5 terminal.

        Args:
            symbol (str): The ticker symbol of the instrument.
            action (int): The action of the order (e.g., mt5.ORDER_BUY, mt5.ORDER_SELL).
            volume (float): The volume of the order (e.g., 1 lot of a future mini-contract)
            order_type (int): The type of the order (e.g., mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_SELL).

        Returns:
            int: The order ticket number.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected to MetaTrader 5 terminal.")
                return None
        
        point = mt5.symbol_info(symbol).point
        price = mt5.symbol_info_tick(symbol).ask #if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).bid
        deviation = 20

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
        #print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,volume,price,deviation));
        print(f"Ordem enviada: {volume} lote de {symbol} ao preço de {price} com desvio de {deviation} pontos")
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
    
    def close_position(self, position_id):
        """
        Closes an open position in the MetaTrader 5 terminal.

        Args:
            position_id (int): The position ticket number.

        Returns:
            bool: True if the position was closed successfully, False otherwise.
        """
        if not self.connected:
            try:
                self.connect()
            except Exception as e:
                print("Error: Not connected to MetaTrader 5 terminal.")
                return False
            
        price=mt5.symbol_info_tick(symbol).bid
        deviation=20
        request={
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "position": position_id,
            "price": price,
            "deviation": deviation,
            "magic": 234000,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        # enviamos a solicitação de negociação
        result=mt5.order_send(request)
        # verificamos o resultado da execução
        print("3. close position #{}: sell {} {} lots at {} with deviation={} points".format(position_id,symbol,lot,price,deviation));
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("4. order_send failed, retcode={}".format(result.retcode))
            print("   result",result)
        else:
            print("4. position #{} closed, {}".format(position_id,result))
        # solicitamos o resultado na forma de dicionário e exibimos elemento por elemento
            result_dict=result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field,result_dict[field]))
                #se esta for uma estrutura de uma solicitação de negociação, também a exibiremos elemento a elemento
                if field=="request":
                    traderequest_dict=result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))

        result = mt5.position_close(position_id)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Error closing position: {result.comment}")
            return False

        return True

#place_market_order("WINM24", mt5.TRADE_ACTION_DEAL, 1.0, mt5.ORDER_TYPE_BUY)