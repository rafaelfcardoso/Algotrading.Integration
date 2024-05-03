import datetime
import time

import MetaTrader5 as mt5
import pytz

from data_source.data_providers import data_provider_factory
from execution.execution_handler import ExecutionHandler
from execution.meta_trader_handler import MetaTraderExecutionHandler
from risk_management.risk_manager import RiskManagement
from strategies.bovespa_index_mini import MiniIndiceBovespa
from strategies.mean_reversion import MeanReversionStrategy


def main():
    # # Initialize components
    config = {
        'data_provider': 'metatrader',
        'api_key': None
    }

    data_provider = data_provider_factory(config['data_provider'])

    metatrader = MetaTraderExecutionHandler()
    risk_manager = RiskManagement()

    # initialize = data_provider.connect()
    # ohlc_data = data_provider.get_previous_candles('WINM24', mt5.TIMEFRAME_M1, count=3)
    # print(ohlc_data)

    # Testing orders:
    # buy_order_market = metatrader.market_buy_order("WINM24", 1.0)
    # sell_order_market = metatrader.market_sell_order("WINM24", 1.0)

    position = risk_manager.get_positions()
    # if position is not None:
    #     print("Posicao encontrada. {} lotes de {}.".format(position['volume'][0], position['symbol'][0]))

    if position is not None:
        print("Posicao encontrada. {} lotes de {}.".format(position['volume'][0], position['symbol'][0]))

        close_position = metatrader.close_position(
            position.loc[0, 'ticket'].astype(int),
            position.loc[0, 'symbol'],
            position.loc[0, 'volume'].astype(float)
        )

    strategy_instance = MeanReversionStrategy(symbol='WINM24', lookback_period=20, entry_threshold=2, exit_threshold=1,
                                              lot_size=1.0)

    # Run the strategy
    poll_interval = 30
    while True:
        now = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))  # Timezone for GMT-3
        real_time_price = data_provider.get_realtime_data('WINM24')

        # If time is 6:25PM or later, stop the loop
        if (now.hour, now.minute) >= (18, 25):
            print("Operacoes finalizadas para o dia.")
            break

        signal = strategy_instance.generate_signal(real_time_price)
        strategy_instance.execute_signal(signal, metatrader)
        time.sleep(poll_interval)


if __name__ == '__main__':
    main()
