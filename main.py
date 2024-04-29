import MetaTrader5 as mt5
from data_source.data_providers import data_provider_factory
from execution.execution_handler import ExecutionHandler
from execution.meta_trader_handler import MetaTraderExecutionHandler
from risk_management.risk_manager import RiskManagement
from strategies.bovespa_index_mini import MiniIndiceBovespa

def main():
    # # Initialize components
    config = {
    'data_provider': 'meta_trader',
    'api_key': None
    }

    data_provider = data_provider_factory(config['data_provider'])

    metatrader = MetaTraderExecutionHandler()
    risk_manager = RiskManagement()

    #initialize = data_provider.connect()
    ohlc_data = data_provider.get_ohlc('WINM24', mt5.TIMEFRAME_M1, n = 3)
    real_time = data_provider.get_realtime_data('WINM24')
    print(real_time)

    #buy_order_market = metatrader.market_buy_order("WINM24", 1.0)
    sell_order_market = metatrader.market_sell_order("WINM24", 1.0)

    position = risk_manager.get_positions()

    #print("symbol:", position['symbol'][0])

    if position is not None:
        print("Posicao encontrada. {} lotes de {}.".format(position['volume'][0], position['symbol'][0]))

        close_position = metatrader.close_position(
            position.loc[0, 'ticket'].astype(int),
            position.loc[0, 'symbol'],
            position.loc[0, 'volume'].astype(float)
        )
    
    #realtime_price = data_provider.get_realtime_data('AAPL')
    # data_provider = DataProvider()
    # execution_handler = ExecutionHandler(broker_api)
    # strategy = MiniIndiceBovespa(data_provider, execution_handler)
    
    # # Run the strategy
    # strategy.run()


if __name__ == '__main__':
    main()