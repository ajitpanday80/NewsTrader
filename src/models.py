"""
Data models for NewsTrader application.
Defines the structure of signals, news articles, and analysis results.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class InstrumentType(str, Enum):
    """Financial instrument types."""
    STOCK = "stock"
    CRYPTOCURRENCY = "cryptocurrency"
    FOREX = "forex"
    ETF = "etf"
    INDEX = "index"
    COMMODITY = "commodity"


class SentimentLabel(str, Enum):
    """Sentiment classification labels."""
    BEARISH = "Bearish"
    SOMEWHAT_BEARISH = "Somewhat-Bearish"
    NEUTRAL = "Neutral"
    SOMEWHAT_BULLISH = "Somewhat-Bullish"
    BULLISH = "Bullish"


class Sentiment(BaseModel):
    """Sentiment score and label."""
    score: float
    label: str


class Asset(BaseModel):
    """Financial asset information."""
    ticker: str
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    market: str
    country: str
    currency: str
    relevance_score: Optional[float] = None
    sentiment: Optional[Sentiment] = None


class RelatedAsset(BaseModel):
    """Related asset identified by AI."""
    ticker: str
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    market: str
    country: str
    currency: str
    relationship: str
    potential_impact: str
    impact_probability: float
    ai_reasoning: str


class TradingSignal(BaseModel):
    """Trading signal with detailed information."""
    signal_id: str
    ticker: str
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    market: str
    country: str
    currency: str
    current_price: Optional[float] = None
    signal: SignalType
    confidence: float
    strength: str
    timeframe: str
    holding_period: str
    entry_strategy: str
    target_allocation: str
    price_target: Optional[float] = None
    stop_loss: Optional[float] = None
    reasoning: str
    risk_factors: List[str]
    catalysts: List[str]
    generated_at: datetime
    expires_at: datetime
    status: str = "active"
    time_remaining_minutes: Optional[int] = None
    is_expired: bool = False


class MarketImpact(BaseModel):
    """Market impact analysis."""
    sectors_affected: List[str]
    impact_level: str
    geographic_impact: List[str]
    market_sentiment_shift: str
    volatility_expectation: str
    expected_duration: str


class NewsArticle(BaseModel):
    """News article with analysis."""
    article_id: str
    title: str
    summary: str
    url: Optional[str] = None
    source: str
    authors: Optional[List[str]] = None
    published_at: datetime
    processed_at: datetime
    expires_at: datetime
    time_remaining_minutes: Optional[int] = None
    topics: Optional[List[str]] = None
    overall_sentiment: Sentiment
    mentioned_assets: List[Asset]
    related_assets: List[RelatedAsset]
    trading_signals: List[TradingSignal]
    market_impact: MarketImpact


class AnalysisMetadata(BaseModel):
    """Metadata for analysis results."""
    analysis_id: str
    timestamp: datetime
    expires_at: datetime
    ttl_minutes: int
    status: str = "active"
    news_source: str
    ai_model: str
    total_articles_analyzed: int
    total_signals_generated: int
    markets_covered: List[str]
    analysis_timeframe: str
    backup_path: Optional[str] = None
    will_be_archived_at: datetime


class SignalBreakdown(BaseModel):
    """Signal breakdown by type."""
    total: int
    BUY: int
    SELL: int
    HOLD: int


class HighConfidenceSignal(BaseModel):
    """High confidence signal summary."""
    ticker: str
    symbol: str
    name: str
    exchange: str
    market: str
    signal: SignalType
    confidence: float


class TopOpportunity(BaseModel):
    """Top trading opportunity."""
    ticker: str
    market: str
    exchange: str
    signal: SignalType
    confidence: float
    reason: str


class TopRisk(BaseModel):
    """Top risk signal."""
    ticker: str
    market: str
    exchange: str
    signal: SignalType
    confidence: float
    reason: str


class AnalysisSummary(BaseModel):
    """Summary of analysis results."""
    total_assets_analyzed: int
    signals_by_type: SignalBreakdown
    signals_by_instrument: Dict[str, SignalBreakdown]
    signals_by_market: Dict[str, SignalBreakdown]
    signals_by_exchange: Dict[str, SignalBreakdown]
    average_confidence: float
    high_confidence_signals: List[HighConfidenceSignal]
    key_insights: List[str]
    top_opportunities: List[TopOpportunity]
    top_risks: List[TopRisk]


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    analysis_metadata: AnalysisMetadata
    news_articles: List[NewsArticle]
    summary: AnalysisSummary


class BackupMetadata(BaseModel):
    """Metadata for backed up analysis."""
    original_analysis_id: str
    archived_at: datetime
    original_timestamp: datetime
    reason: str
    ttl_minutes: int


class BackupData(BaseModel):
    """Backed up analysis data."""
    backup_metadata: BackupMetadata
    original_data: AnalysisResult
