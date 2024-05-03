from datetime import datetime
import MetaTrader5 as mt5
import time
import pytz
from pytz import timezone

from data_source.data_providers import data_provider_factory
from execution.execution_handler import ExecutionHandler
from execution.meta_trader_handler import MetaTraderExecutionHandler
from risk_management.risk_manager import RiskManagement
from strategies.mean_reversion import MeanReversionStrategy


def main():
    # display data on MetaTrader 5 version
    # # Initialize components
    config = {
        'data_provider': 'metatrader',
        'api_key': None
    }
    data_provider = data_provider_factory(config['data_provider'])
    symbol = 'WINM24'  # Bovespa Mini Index Futures symbol - '^BVSP' from Yahoo or 'WINM24' from metatrader
    interval = mt5.TIMEFRAME_M1  # interval, mt5.TIMEFRAME_M1 for 1 minute time frame

    gmt = pytz.timezone("Etc/GMT-3")
    start_date = '2024-05-03'
    end_date = '2024-05-04'
    all_candles = data_provider.get_historical_data(symbol, start_date, end_date, interval)

    metatrader = MetaTraderExecutionHandler()
    risk_manager = RiskManagement()

    # previous_n_candles = data_provider.get_previous_candles(symbol, mt5.TIMEFRAME_M1, count=20)
    # print('previous_n_candles', previous_n_candles)

    # real_time = data_provider.get_realtime_data(symbol)
    # print(real_time)
    # Testing orders:
    # buy_order_market = metatrader.market_buy_order(symbol, 1.0)
    # sell_order_market = metatrader.market_sell_order(symbol, 1.0)

    # Run the strategy
    now = datetime.now(pytz.timezone('America/Sao_Paulo'))  # Timezone for GMT-3
    poll_interval = 1
    strategy = MeanReversionStrategy(symbol, lookback_period=20, entry_threshold=2, exit_threshold=1,
                                     lot_size=1.0)
    while True:
        data = data_provider.get_previous_candles(symbol, mt5.TIMEFRAME_M1, count=20)

        # If time is 6:25PM or later, stop the loop
        if (now.hour, now.minute) >= (18, 25):
            print("Operacoes finalizadas para o dia.")
            break

        signal = strategy.generate_signal(data)

        strategy.execute_signal(signal, metatrader)
        time.sleep(poll_interval)

    # position = risk_manager.get_positions()
    # if position is not None:
    #     print("Posicao encontrada. {} lotes de {}.".format(position['volume'][0], position['symbol'][0]))

    # if position is not None:
    #     print("Posicao encontrada. {} lotes de {}.".format(position['volume'][0], position['symbol'][0]))
    #
    #     close_position = metatrader.close_position(
    #        position.loc[0, 'ticket'].astype(int),
    #        position.loc[0, 'symbol'],
    #        position.loc[0, 'volume'].astype(float)
    #     )


if __name__ == '__main__':
    main()
