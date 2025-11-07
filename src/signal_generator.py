"""
Signal generator using Groq AI to analyze news and generate trading signals.
Uses openai/gpt-oss-120b model for deep analysis of market news.
"""

import json
import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from groq import Groq

from src.config import settings
from src.models import (
    AnalysisResult, AnalysisMetadata, NewsArticle, TradingSignal,
    Asset, RelatedAsset, Sentiment, MarketImpact, AnalysisSummary,
    SignalBreakdown, HighConfidenceSignal, TopOpportunity, TopRisk, SignalType
)


class SignalGenerator:
    """Generates trading signals from news using Groq AI."""

    def __init__(self, api_key: str, model: str = "openai/gpt-oss-120b"):
        """Initialize signal generator with Groq API key."""
        self.client = Groq(api_key=api_key)
        self.model = model

    def analyze_news_with_ai(self, news_articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze news articles using Groq AI to identify related stocks and generate signals.

        Args:
            news_articles: List of parsed news articles

        Returns:
            AI analysis with related stocks and signals
        """
        # Prepare prompt for AI
        prompt = self._create_analysis_prompt(news_articles)

        try:
            logger.info(f"Sending {len(news_articles)} articles to Groq AI for analysis")

            # Call Groq AI
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert financial analyst and trading strategist.
                        Your task is to analyze market news and generate actionable trading signals.

                        For each news article:
                        1. Identify all stocks/assets mentioned (from the ticker_sentiment data)
                        2. Identify related/correlated stocks that may be affected but NOT mentioned
                        3. Analyze the potential market impact
                        4. Generate BUY/SELL/HOLD signals with confidence scores
                        5. Provide clear reasoning for each signal
                        6. Identify risk factors and catalysts

                        Consider:
                        - Direct competitors
                        - Supply chain relationships (suppliers, manufacturers)
                        - Industry sector correlations
                        - Market indices
                        - Currency and commodity impacts
                        - Institutional holdings

                        Return your analysis as a JSON object."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=8000,
                response_format={"type": "json_object"}
            )

            # Parse AI response
            ai_response = chat_completion.choices[0].message.content
            analysis = json.loads(ai_response)

            logger.info("Successfully received AI analysis from Groq")
            return analysis

        except Exception as e:
            logger.error(f"Error calling Groq AI: {e}")
            return {"articles": []}

    def _create_analysis_prompt(self, news_articles: List[Dict[str, Any]]) -> str:
        """Create detailed prompt for AI analysis."""

        articles_summary = []
        for idx, article in enumerate(news_articles, 1):
            article_info = {
                "article_number": idx,
                "title": article.get("title", ""),
                "summary": article.get("summary", ""),
                "source": article.get("source", ""),
                "published_at": article.get("time_published", datetime.utcnow()).isoformat(),
                "overall_sentiment_score": article.get("overall_sentiment_score", 0.0),
                "overall_sentiment_label": article.get("overall_sentiment_label", "Neutral"),
                "topics": article.get("topics", []),
                "mentioned_tickers": []
            }

            # Add ticker sentiments
            for ticker_data in article.get("ticker_sentiment", []):
                article_info["mentioned_tickers"].append({
                    "ticker": ticker_data.get("ticker", ""),
                    "relevance_score": ticker_data.get("relevance_score", 0.0),
                    "sentiment_score": ticker_data.get("ticker_sentiment_score", 0.0),
                    "sentiment_label": ticker_data.get("ticker_sentiment_label", "Neutral")
                })

            articles_summary.append(article_info)

        prompt = f"""Analyze the following {len(news_articles)} market news articles and generate trading signals.

NEWS ARTICLES:
{json.dumps(articles_summary, indent=2)}

For each article, provide:

1. **Related Assets**: Identify stocks/assets NOT mentioned in the article but likely to be affected:
   - Competitors (may lose market share)
   - Suppliers/Partners (may benefit from increased business)
   - Industry peers (sector correlation)
   - Related indices, ETFs, commodities, currencies

2. **Trading Signals**: For BOTH mentioned and related assets, generate:
   - Signal: BUY, SELL, or HOLD
   - Confidence: 0.0 to 1.0
   - Strength: strong, moderate, weak
   - Timeframe: short-term, medium-term, long-term
   - Clear reasoning
   - Risk factors (what could go wrong)
   - Catalysts (what supports this signal)

3. **Market Impact**: Overall impact on sectors and markets

Return JSON in this EXACT format:
{{
  "articles": [
    {{
      "article_number": 1,
      "related_assets": [
        {{
          "ticker": "TICKER",
          "name": "Company Name",
          "instrument_type": "stock|cryptocurrency|forex|etf|index",
          "exchange": "NYSE|NASDAQ|NSE|BSE|Multiple Exchanges|Forex Market",
          "market": "US|India|Crypto|Forex|Global",
          "country": "USA|India|Global",
          "currency": "USD|INR",
          "relationship": "competitor|supplier|partner|sector_correlation|alternative_asset",
          "potential_impact": "positive|negative|mixed",
          "impact_probability": 0.75,
          "reasoning": "Why this asset is affected"
        }}
      ],
      "trading_signals": [
        {{
          "ticker": "TICKER",
          "name": "Asset Name",
          "instrument_type": "stock|cryptocurrency|forex|etf|index",
          "exchange": "NYSE|NASDAQ|NSE|BSE|Multiple Exchanges|Forex Market",
          "market": "US|India|Crypto|Forex|Global",
          "country": "USA|India|Global",
          "currency": "USD|INR",
          "signal": "BUY|SELL|HOLD",
          "confidence": 0.85,
          "strength": "strong|moderate|weak",
          "timeframe": "short-term|medium-term|long-term",
          "holding_period": "1-4 weeks|1-3 months|3-12 months",
          "entry_strategy": "immediate|gradual|wait",
          "target_allocation": "5-10%|hold_existing|reduce_exposure",
          "reasoning": "Clear explanation",
          "risk_factors": ["Risk 1", "Risk 2"],
          "catalysts": ["Catalyst 1", "Catalyst 2"],
          "is_mentioned_in_article": true
        }}
      ],
      "market_impact": {{
        "sectors_affected": ["Technology", "Finance"],
        "impact_level": "high|moderate|low",
        "geographic_impact": ["USA", "India", "Global"],
        "market_sentiment_shift": "bullish|bearish|neutral|risk-on|risk-off",
        "volatility_expectation": "high|moderate|low",
        "expected_duration": "1-2 weeks|1-3 months"
      }}
    }}
  ],
  "key_insights": ["Insight 1", "Insight 2", "Insight 3"]
}}

Be specific with exchange names (NYSE, NASDAQ, NSE, BSE, etc.) and ensure all fields are filled."""

        return prompt

    def generate_signals(self, news_articles: List[Dict[str, Any]]) -> AnalysisResult:
        """
        Generate complete analysis result from news articles.

        Args:
            news_articles: List of parsed news articles from Alpha Vantage

        Returns:
            Complete AnalysisResult object
        """
        if not news_articles:
            logger.warning("No news articles to analyze")
            return self._create_empty_result()

        # Get AI analysis
        ai_analysis = self.analyze_news_with_ai(news_articles)

        # Generate timestamps
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=settings.signal_ttl_minutes)
        analysis_id = str(uuid.uuid4())

        # Build result
        result_articles = []
        all_signals = []
        markets_covered = set()

        for article_data, ai_article in zip(news_articles, ai_analysis.get("articles", [])):
            article_id = str(uuid.uuid4())

            # Parse mentioned assets
            mentioned_assets = []
            for ticker_data in article_data.get("ticker_sentiment", []):
                asset = Asset(
                    ticker=ticker_data.get("ticker", ""),
                    symbol=ticker_data.get("ticker", ""),
                    name=self._get_asset_name(ticker_data.get("ticker", "")),
                    instrument_type=self._detect_instrument_type(ticker_data.get("ticker", "")),
                    exchange=self._get_exchange(ticker_data.get("ticker", "")),
                    market=self._get_market(ticker_data.get("ticker", "")),
                    country=self._get_country(ticker_data.get("ticker", "")),
                    currency=self._get_currency(ticker_data.get("ticker", "")),
                    relevance_score=ticker_data.get("relevance_score", 0.0),
                    sentiment=Sentiment(
                        score=ticker_data.get("ticker_sentiment_score", 0.0),
                        label=ticker_data.get("ticker_sentiment_label", "Neutral")
                    )
                )
                mentioned_assets.append(asset)
                markets_covered.add(asset.market)

            # Parse related assets from AI
            related_assets = []
            for related_data in ai_article.get("related_assets", []):
                related_asset = RelatedAsset(**related_data)
                related_assets.append(related_asset)
                markets_covered.add(related_data.get("market", "Global"))

            # Parse trading signals from AI
            trading_signals = []
            for signal_data in ai_article.get("trading_signals", []):
                signal_id = str(uuid.uuid4())

                trading_signal = TradingSignal(
                    signal_id=signal_id,
                    ticker=signal_data.get("ticker", ""),
                    symbol=signal_data.get("ticker", ""),
                    name=signal_data.get("name", ""),
                    instrument_type=signal_data.get("instrument_type", "stock"),
                    exchange=signal_data.get("exchange", "Unknown"),
                    market=signal_data.get("market", "Global"),
                    country=signal_data.get("country", "Global"),
                    currency=signal_data.get("currency", "USD"),
                    signal=SignalType(signal_data.get("signal", "HOLD")),
                    confidence=signal_data.get("confidence", 0.5),
                    strength=signal_data.get("strength", "moderate"),
                    timeframe=signal_data.get("timeframe", "short-term"),
                    holding_period=signal_data.get("holding_period", "1-4 weeks"),
                    entry_strategy=signal_data.get("entry_strategy", "gradual"),
                    target_allocation=signal_data.get("target_allocation", "hold_existing"),
                    reasoning=signal_data.get("reasoning", ""),
                    risk_factors=signal_data.get("risk_factors", []),
                    catalysts=signal_data.get("catalysts", []),
                    generated_at=now,
                    expires_at=expires_at,
                    status="active",
                    time_remaining_minutes=settings.signal_ttl_minutes,
                    is_expired=False
                )
                trading_signals.append(trading_signal)
                all_signals.append(trading_signal)

            # Create news article object
            news_article = NewsArticle(
                article_id=article_id,
                title=article_data.get("title", ""),
                summary=article_data.get("summary", ""),
                url=article_data.get("url", None),
                source=article_data.get("source", "Unknown"),
                authors=article_data.get("authors", []),
                published_at=article_data.get("time_published", now),
                processed_at=now,
                expires_at=expires_at,
                time_remaining_minutes=settings.signal_ttl_minutes,
                topics=article_data.get("topics", []),
                overall_sentiment=Sentiment(
                    score=article_data.get("overall_sentiment_score", 0.0),
                    label=article_data.get("overall_sentiment_label", "Neutral")
                ),
                mentioned_assets=mentioned_assets,
                related_assets=related_assets,
                trading_signals=trading_signals,
                market_impact=MarketImpact(**ai_article.get("market_impact", {
                    "sectors_affected": [],
                    "impact_level": "moderate",
                    "geographic_impact": [],
                    "market_sentiment_shift": "neutral",
                    "volatility_expectation": "moderate",
                    "expected_duration": "1-2 weeks"
                }))
            )
            result_articles.append(news_article)

        # Build metadata
        backup_path = f"backups/{now.strftime('%Y-%m-%d')}/analysis-{analysis_id}.json"
        metadata = AnalysisMetadata(
            analysis_id=analysis_id,
            timestamp=now,
            expires_at=expires_at,
            ttl_minutes=settings.signal_ttl_minutes,
            status="active",
            news_source="Alpha Vantage",
            ai_model=self.model,
            total_articles_analyzed=len(news_articles),
            total_signals_generated=len(all_signals),
            markets_covered=sorted(list(markets_covered)),
            analysis_timeframe="latest",
            backup_path=backup_path,
            will_be_archived_at=expires_at
        )

        # Build summary
        summary = self._build_summary(all_signals, ai_analysis.get("key_insights", []))

        return AnalysisResult(
            analysis_metadata=metadata,
            news_articles=result_articles,
            summary=summary
        )

    def _build_summary(self, signals: List[TradingSignal], key_insights: List[str]) -> AnalysisSummary:
        """Build summary statistics from signals."""

        # Count signals by type
        buy_count = sum(1 for s in signals if s.signal == SignalType.BUY)
        sell_count = sum(1 for s in signals if s.signal == SignalType.SELL)
        hold_count = sum(1 for s in signals if s.signal == SignalType.HOLD)

        signals_by_type = SignalBreakdown(
            total=len(signals),
            BUY=buy_count,
            SELL=sell_count,
            HOLD=hold_count
        )

        # Group by instrument type
        signals_by_instrument = {}
        for signal in signals:
            inst_type = signal.instrument_type
            if inst_type not in signals_by_instrument:
                signals_by_instrument[inst_type] = {"BUY": 0, "SELL": 0, "HOLD": 0}
            signals_by_instrument[inst_type][signal.signal.value] += 1

        for inst_type in signals_by_instrument:
            counts = signals_by_instrument[inst_type]
            signals_by_instrument[inst_type] = SignalBreakdown(
                total=counts["BUY"] + counts["SELL"] + counts["HOLD"],
                BUY=counts["BUY"],
                SELL=counts["SELL"],
                HOLD=counts["HOLD"]
            )

        # Group by market
        signals_by_market = {}
        for signal in signals:
            market = signal.market
            if market not in signals_by_market:
                signals_by_market[market] = {"BUY": 0, "SELL": 0, "HOLD": 0}
            signals_by_market[market][signal.signal.value] += 1

        for market in signals_by_market:
            counts = signals_by_market[market]
            signals_by_market[market] = SignalBreakdown(
                total=counts["BUY"] + counts["SELL"] + counts["HOLD"],
                BUY=counts["BUY"],
                SELL=counts["SELL"],
                HOLD=counts["HOLD"]
            )

        # Group by exchange
        signals_by_exchange = {}
        for signal in signals:
            exchange = signal.exchange
            if exchange not in signals_by_exchange:
                signals_by_exchange[exchange] = {"BUY": 0, "SELL": 0, "HOLD": 0}
            signals_by_exchange[exchange][signal.signal.value] += 1

        for exchange in signals_by_exchange:
            counts = signals_by_exchange[exchange]
            signals_by_exchange[exchange] = SignalBreakdown(
                total=counts["BUY"] + counts["SELL"] + counts["HOLD"],
                BUY=counts["BUY"],
                SELL=counts["SELL"],
                HOLD=counts["HOLD"]
            )

        # High confidence signals
        high_conf_signals = sorted(
            [s for s in signals if s.confidence >= 0.75],
            key=lambda x: x.confidence,
            reverse=True
        )[:5]

        high_confidence_signals = [
            HighConfidenceSignal(
                ticker=s.ticker,
                symbol=s.symbol,
                name=s.name,
                exchange=s.exchange,
                market=s.market,
                signal=s.signal,
                confidence=s.confidence
            )
            for s in high_conf_signals
        ]

        # Top opportunities (high confidence BUY)
        buy_signals = sorted(
            [s for s in signals if s.signal == SignalType.BUY],
            key=lambda x: x.confidence,
            reverse=True
        )[:3]

        top_opportunities = [
            TopOpportunity(
                ticker=s.ticker,
                market=s.market,
                exchange=s.exchange,
                signal=s.signal,
                confidence=s.confidence,
                reason=s.reasoning[:100] + "..."
            )
            for s in buy_signals
        ]

        # Top risks (high confidence SELL)
        sell_signals = sorted(
            [s for s in signals if s.signal == SignalType.SELL],
            key=lambda x: x.confidence,
            reverse=True
        )[:3]

        top_risks = [
            TopRisk(
                ticker=s.ticker,
                market=s.market,
                exchange=s.exchange,
                signal=s.signal,
                confidence=s.confidence,
                reason=s.reasoning[:100] + "..."
            )
            for s in sell_signals
        ]

        # Average confidence
        avg_confidence = sum(s.confidence for s in signals) / len(signals) if signals else 0.0

        return AnalysisSummary(
            total_assets_analyzed=len(set(s.ticker for s in signals)),
            signals_by_type=signals_by_type,
            signals_by_instrument=signals_by_instrument,
            signals_by_market=signals_by_market,
            signals_by_exchange=signals_by_exchange,
            average_confidence=round(avg_confidence, 2),
            high_confidence_signals=high_confidence_signals,
            key_insights=key_insights,
            top_opportunities=top_opportunities,
            top_risks=top_risks
        )

    def _create_empty_result(self) -> AnalysisResult:
        """Create empty result when no news available."""
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=settings.signal_ttl_minutes)

        return AnalysisResult(
            analysis_metadata=AnalysisMetadata(
                analysis_id=str(uuid.uuid4()),
                timestamp=now,
                expires_at=expires_at,
                ttl_minutes=settings.signal_ttl_minutes,
                status="active",
                news_source="Alpha Vantage",
                ai_model=self.model,
                total_articles_analyzed=0,
                total_signals_generated=0,
                markets_covered=[],
                analysis_timeframe="latest",
                will_be_archived_at=expires_at
            ),
            news_articles=[],
            summary=AnalysisSummary(
                total_assets_analyzed=0,
                signals_by_type=SignalBreakdown(total=0, BUY=0, SELL=0, HOLD=0),
                signals_by_instrument={},
                signals_by_market={},
                signals_by_exchange={},
                average_confidence=0.0,
                high_confidence_signals=[],
                key_insights=[],
                top_opportunities=[],
                top_risks=[]
            )
        )

    # Helper methods for asset information
    def _get_asset_name(self, ticker: str) -> str:
        """Get asset name from ticker (simplified)."""
        return ticker

    def _detect_instrument_type(self, ticker: str) -> str:
        """Detect instrument type from ticker."""
        if ticker.startswith("CRYPTO:"):
            return "cryptocurrency"
        elif ticker.startswith("FOREX:"):
            return "forex"
        else:
            return "stock"

    def _get_exchange(self, ticker: str) -> str:
        """Get exchange from ticker (simplified)."""
        if ticker.startswith("CRYPTO:"):
            return "Multiple Exchanges"
        elif ticker.startswith("FOREX:"):
            return "Forex Market"
        else:
            return "Unknown"

    def _get_market(self, ticker: str) -> str:
        """Get market from ticker."""
        if ticker.startswith("CRYPTO:"):
            return "Crypto"
        elif ticker.startswith("FOREX:"):
            return "Forex"
        else:
            return "Global"

    def _get_country(self, ticker: str) -> str:
        """Get country from ticker."""
        if ticker.startswith("CRYPTO:") or ticker.startswith("FOREX:"):
            return "Global"
        else:
            return "USA"

    def _get_currency(self, ticker: str) -> str:
        """Get currency from ticker."""
        if ticker.startswith("CRYPTO:") or ticker.startswith("FOREX:"):
            return "USD"
        else:
            return "USD"


# Global instance
signal_generator = SignalGenerator(
    api_key=settings.groq_api_key,
    model=settings.groq_model
)
