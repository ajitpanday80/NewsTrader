"""
NewsTrader - AI-Powered News-Based Stock Signal Generator

Analyzes market news using Alpha Vantage API and generates trading signals
using Groq AI (openai/gpt-oss-120b model).

Supports multiple asset classes:
- Stocks (US, India, Global)
- Cryptocurrencies
- Forex
- ETFs
- Indices

Signals automatically expire after configurable TTL (default 30 minutes)
and are backed up before removal.
"""

__version__ = "1.0.0"
__author__ = "NewsTrader Team"

from src.config import settings
from src.news_fetcher import news_fetcher
from src.signal_generator import signal_generator
from src.cleanup_service import cleanup_service

__all__ = [
    "settings",
    "news_fetcher",
    "signal_generator",
    "cleanup_service"
]
