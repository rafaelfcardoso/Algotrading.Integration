from data.data_provider import DataProvider
from strategies.bovespa_index_mini import BrazilFuturesStrategy
from backtesting.backtesting_engine import BacktestingEngine

def run_backtesting():
    # Prepare historical data
    data_provider = DataProvider()
    historical_data = data_provider.get_historical_data('SYMBOL', start_date='2022-01-01', end_date='2022-12-31')
    
    # Instantiate the trading strategy
    strategy = BrazilFuturesStrategy()
    
    # Create the backtesting engine
    backtesting_engine = BacktestingEngine(historical_data, strategy)
    
    # Run the backtesting simulation
    backtesting_results = backtesting_engine.run()
    
    # Analyze the backtesting results
    print(backtesting_results)
    # Perform further analysis, visualization, and evaluation of the results

if __name__ == '__main__':
    run_backtesting()