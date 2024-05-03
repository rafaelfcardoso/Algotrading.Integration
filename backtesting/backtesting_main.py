import sys

sys.path.append('f:\\Repos\\Algotrading.Integration')
from data_source.data_providers import data_provider_factory
from backtesting.backtester import Backtester
from strategies.mean_reversion import MeanReversionStrategy

sys.path.append('f:\\Repos\\Algotrading.Integration')


def run_backtesting():
    # # Initialize components
    config = {
        'data_provider': 'metatrader',
        'api_key': None
    }

    data_provider = data_provider_factory(config['data_provider'])

    # Prepare historical data
    symbol = 'WINM24'  # Bovespa Mini Index Futures symbol - '^BVSP' from Yahoo or 'WINM24' from metatrader
    start_date = '2024-05-03'
    end_date = '2024-05-04'

    historical_data = data_provider.get_historical_data(symbol, start_date, end_date)
    print(historical_data.head())

    # Instantiate the trading strategy
    strategy = MeanReversionStrategy(symbol='WINM24', lookback_period=20, entry_threshold=2, exit_threshold=1,
                                     lot_size=1.0)

    # Create an instance of the MeanReversionBacktester
    backtester = Backtester(strategy, lot_size=1.0, stop_loss=100)

    # Run the backtesting simulation
    lookback_period = 20
    backtest_results = backtester.run(historical_data)

    # Analyze the backtesting results
    print(backtest_results[1])

    # Perform further analysis, visualization, and evaluation of the results
    backtest_results[0].to_csv(f"resultado_{symbol}_inicio_{start_date}_fim_{end_date}.csv", index=True)


if __name__ == '__main__':
    run_backtesting()
