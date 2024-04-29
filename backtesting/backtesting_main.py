from data.data_providers import data_provider_factory
from mean_reversion import MeanReversionBacktester
from strategies.mean_reversion import MeanReversionStrategy


def run_backtesting():
    # # Initialize components
    config = {
        'data_provider': 'meta_trader',
        'api_key': None
    }

    # Prepare historical data
    data_provider = data_provider_factory(config['data_provider'])
    historical_data = data_provider.get_historical_data('WINM24', start_date='2024-04-25', end_date='2024-04-26')

    # Instantiate the trading strategy
    strategy = MeanReversionStrategy(symbol='WINM24', lookback_period=20, entry_threshold=2, exit_threshold=1,
                                     lot_size=0.1)

    # Create an instance of the MeanReversionBacktester
    backtester = MeanReversionBacktester(strategy)

    # Run the backtesting simulation
    backtest_results = backtester.run(historical_data)

    # Analyze the backtesting results
    print(backtest_results)
    # Perform further analysis, visualization, and evaluation of the results


if __name__ == '__main__':
    run_backtesting()
