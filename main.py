from trade import AITrader, broker
from datetime import datetime
from lumibot.backtesting import YahooDataBacktesting
from lumibot.traders import Trader


def init_strategy(broker, stock):
    strategy = AITrader(
        name="investbot",
        broker=broker,
        parameters={"symbol": stock, "cash_at_risk": 0.5},
    )
    return strategy


def backtest(strategy, backtesting, start_date, end_date, stock):
    strategy.backtest(
        backtesting,
        start_date,
        end_date,
        parameters={"symbol": stock, "cash_at_risk": 0.5},
    )


def trade(strategy):
    trader = Trader()
    trader.add_strategy(strategy)
    trader.run_all()


if __name__ == "__main__":
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)

    strategy = init_strategy(
        broker=broker,
        stock="SPY",
    )

    backtest(
        strategy=strategy,
        backtesting=YahooDataBacktesting,
        start_date=start_date,
        end_date=end_date,
        stock="SPY",
    )
