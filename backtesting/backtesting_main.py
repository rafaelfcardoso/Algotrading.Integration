import sys
sys.path.append('f:\\Repos\\Algotrading.Integration')
from data_source.data_providers import data_provider_factory
from backtesting.mean_reversion import MeanReversionBacktester
from strategies.mean_reversion import MeanReversionStrategy


sys.path.append('f:\\Repos\\Algotrading.Integration')

def run_backtesting():
    # # Initialize components
    config = {
        'data_provider': 'yfinance',
        'api_key': None
    }
    
    data_provider = data_provider_factory(config['data_provider'])

    # Prepare historical data
    symbol = '^BVSP'  # Bovespa Mini Index Futures symbol
    start_date = '2020-01-01'
    end_date = '2021-12-31'

    historical_data = data_provider.get_historical_data('^BVSP', start_date, end_date)
    print(historical_data.head())

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
