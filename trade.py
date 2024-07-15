import os
import logging

from alpaca_trade_api.rest import URL
from dotenv import load_dotenv
from alpaca_trade_api import REST
from lumibot.brokers import Alpaca
from lumibot.strategies.strategy import Strategy
from timedelta import Timedelta

from llm import estimate_sentiment

logger = logging.getLogger(__name__)
load_dotenv()
try:
    ALPACA_API_KEY = os.environ["ALPACA_API_KEY"]
    ALPACA_API_SECRET = os.environ["ALPACA_API_SECRET"]
    ALPACA_API_URL = URL(os.environ["ALPACA_API_URL"])
    ALPACA_CREDS = {
        "API_KEY": ALPACA_API_KEY,
        "API_SECRET": ALPACA_API_SECRET,
        "PAPER": True,
    }
    broker = Alpaca(ALPACA_CREDS)
except KeyError:
    raise RuntimeError("Missing environment variables")


class AITrader(Strategy):
    def initialize(self, symbol: str, cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk
        self.api = REST(
            base_url=ALPACA_API_URL,
            key_id=ALPACA_API_KEY,
            secret_key=ALPACA_API_SECRET,
        )

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self, days_prior=3):
        today = self.get_datetime()
        days_prior = today - Timedelta(days=days_prior)
        return today.strftime("%Y-%m-%d"), days_prior.strftime("%Y-%m-%d")

    def get_sentiment(self):
        today, three_days_prior = self.get_dates(3)
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        analysis = estimate_sentiment(news)
        logger.debug(f"analysis: {analysis}")
        return analysis["probability"], analysis["sentiment"]

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > 0.9:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price * 1.20,
                    stop_loss_limit_price=last_price * 0.95,
                )
                self.submit_order(order)
                self.last_trade = "buy"
            elif sentiment == "negative" and probability > 0.9:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price * 0.80,
                    stop_loss_price=last_price * 1.05,
                )
                self.submit_order(order)
                self.last_trade = "sell"
