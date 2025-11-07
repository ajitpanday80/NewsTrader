"""
News fetcher for Alpha Vantage Market News & Sentiment API.
Fetches latest market news with sentiment data for stocks, crypto, and forex.
"""

import requests
from typing import List, Dict, Optional, Any
from datetime import datetime
from loguru import logger
from src.config import settings


class AlphaVantageNewsFetcher:
    """Fetches news from Alpha Vantage Market News & Sentiment API."""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        """Initialize news fetcher with API key."""
        self.api_key = api_key

    def fetch_latest_news(
        self,
        tickers: Optional[str] = None,
        topics: Optional[str] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        sort: str = "LATEST",
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Fetch latest news from Alpha Vantage.

        Args:
            tickers: Stock/crypto/forex symbols (e.g., "IBM", "CRYPTO:BTC", "FOREX:USD")
            topics: News categories (earnings, ipo, mergers_and_acquisitions, etc.)
            time_from: Start date in YYYYMMDDTHHMM format
            time_to: End date in YYYYMMDDTHHMM format
            sort: LATEST (default), EARLIEST, or RELEVANCE
            limit: Results per query (default 50, max 1000)

        Returns:
            Dict containing news feed and metadata
        """
        params = {
            "function": "NEWS_SENTIMENT",
            "apikey": self.api_key,
            "sort": sort,
            "limit": limit
        }

        # Add optional parameters
        if tickers:
            params["tickers"] = tickers
        if topics:
            params["topics"] = topics
        if time_from:
            params["time_from"] = time_from
        if time_to:
            params["time_to"] = time_to

        try:
            logger.info(f"Fetching news from Alpha Vantage (limit={limit}, sort={sort})")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return {"feed": [], "items": "0", "sentiment_score_definition": ""}

            if "Note" in data:
                logger.warning(f"Alpha Vantage API note: {data['Note']}")
                return {"feed": [], "items": "0", "sentiment_score_definition": ""}

            # Log success
            feed_count = len(data.get("feed", []))
            logger.info(f"Successfully fetched {feed_count} news articles from Alpha Vantage")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news from Alpha Vantage: {e}")
            return {"feed": [], "items": "0", "sentiment_score_definition": ""}

    def fetch_news_by_topics(self, topics: List[str], limit: int = 50) -> Dict[str, Any]:
        """
        Fetch news filtered by specific topics.

        Available topics:
        - earnings
        - ipo
        - mergers_and_acquisitions
        - financial_markets
        - economy_fiscal
        - economy_monetary
        - economy_macro
        - energy_transportation
        - finance
        - life_sciences
        - manufacturing
        - real_estate
        - retail_wholesale
        - technology
        - blockchain

        Args:
            topics: List of topic strings
            limit: Results per query

        Returns:
            Dict containing news feed and metadata
        """
        topics_str = ",".join(topics)
        return self.fetch_latest_news(topics=topics_str, limit=limit)

    def fetch_news_by_tickers(self, tickers: List[str], limit: int = 50) -> Dict[str, Any]:
        """
        Fetch news filtered by specific tickers.

        Args:
            tickers: List of ticker symbols (e.g., ["AAPL", "CRYPTO:BTC", "FOREX:USD"])
            limit: Results per query

        Returns:
            Dict containing news feed and metadata
        """
        tickers_str = ",".join(tickers)
        return self.fetch_latest_news(tickers=tickers_str, limit=limit)

    def parse_news_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single news article from Alpha Vantage response.

        Args:
            article: Raw article dict from API

        Returns:
            Parsed article with standardized fields
        """
        # Parse timestamp
        time_published = article.get("time_published", "")
        try:
            published_at = datetime.strptime(time_published, "%Y%m%dT%H%M%S")
        except (ValueError, TypeError):
            published_at = datetime.utcnow()

        # Parse overall sentiment
        overall_sentiment_score = float(article.get("overall_sentiment_score", 0.0))
        overall_sentiment_label = article.get("overall_sentiment_label", "Neutral")

        # Parse ticker sentiments
        ticker_sentiments = []
        for ticker_data in article.get("ticker_sentiment", []):
            ticker_sentiments.append({
                "ticker": ticker_data.get("ticker", ""),
                "relevance_score": float(ticker_data.get("relevance_score", 0.0)),
                "ticker_sentiment_score": float(ticker_data.get("ticker_sentiment_score", 0.0)),
                "ticker_sentiment_label": ticker_data.get("ticker_sentiment_label", "Neutral")
            })

        # Parse topics
        topics = []
        for topic_data in article.get("topics", []):
            topics.append(topic_data.get("topic", ""))

        return {
            "title": article.get("title", ""),
            "url": article.get("url", None),
            "time_published": published_at,
            "authors": article.get("authors", []),
            "summary": article.get("summary", ""),
            "banner_image": article.get("banner_image", None),
            "source": article.get("source", "Unknown"),
            "category_within_source": article.get("category_within_source", ""),
            "source_domain": article.get("source_domain", ""),
            "topics": topics,
            "overall_sentiment_score": overall_sentiment_score,
            "overall_sentiment_label": overall_sentiment_label,
            "ticker_sentiment": ticker_sentiments
        }

    def get_latest_articles(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get latest news articles with parsed data.

        Args:
            limit: Number of articles to fetch

        Returns:
            List of parsed articles
        """
        data = self.fetch_latest_news(limit=limit)
        articles = []

        for article in data.get("feed", []):
            try:
                parsed_article = self.parse_news_article(article)
                articles.append(parsed_article)
            except Exception as e:
                logger.error(f"Error parsing article: {e}")
                continue

        return articles

    def classify_sentiment(self, score: float) -> str:
        """
        Classify sentiment score into label.

        Sentiment Score Ranges:
        - x <= -0.35: Bearish
        - -0.35 < x <= -0.15: Somewhat-Bearish
        - -0.15 < x < 0.15: Neutral
        - 0.15 <= x < 0.35: Somewhat-Bullish
        - x >= 0.35: Bullish

        Args:
            score: Sentiment score

        Returns:
            Sentiment label string
        """
        if score <= -0.35:
            return "Bearish"
        elif score <= -0.15:
            return "Somewhat-Bearish"
        elif score < 0.15:
            return "Neutral"
        elif score < 0.35:
            return "Somewhat-Bullish"
        else:
            return "Bullish"


# Global instance
news_fetcher = AlphaVantageNewsFetcher(api_key=settings.alpha_vantage_api_key)
