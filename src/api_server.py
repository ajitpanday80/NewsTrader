"""
FastAPI server for serving trading signals to frontend/website.
Provides REST API endpoints for accessing active signals and historical data.
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from src.cleanup_service import cleanup_service
from src.config import settings
from src.auth import verify_api_key, get_api_key_info


# Create FastAPI app
app = FastAPI(
    title="NewsTrader Signal API",
    description="Real-time trading signals based on market news analysis",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "NewsTrader Signal API",
        "version": "1.0.0",
        "description": "Real-time trading signals based on market news analysis",
        "authentication": get_api_key_info(),
        "endpoints": {
            "GET /signals": "Get active trading signals (requires API key)",
            "GET /signals/summary": "Get summary of active signals (requires API key)",
            "GET /signals/history": "Get historical archived signals (requires API key)",
            "GET /signals/backups": "List available backup dates (requires API key)",
            "GET /health": "Health check endpoint (public)"
        },
        "note": "All endpoints except /health require authentication via X-API-Key header"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "NewsTrader API"
    }


@app.get("/signals")
async def get_active_signals(api_key: str = Depends(verify_api_key)):
    """
    Get active trading signals with TTL information.

    Returns only signals that haven't expired yet.
    Each signal includes time_remaining_minutes field.

    Requires:
        X-API-Key header with valid API key

    Returns:
        Active signals with metadata, or empty response if no active signals
    """
    try:
        signals = cleanup_service.get_active_signals_with_ttl()

        if signals is None:
            return {
                "status": "no_active_signals",
                "message": "No active signals available. New signals will be generated when fresh news is analyzed.",
                "data": None
            }

        return {
            "status": "success",
            "data": signals,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting active signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/summary")
async def get_signals_summary(api_key: str = Depends(verify_api_key)):
    """
    Get summary of active signals without full article details.

    Returns condensed information for quick overview.

    Requires:
        X-API-Key header with valid API key

    Returns:
        Summary statistics and high-level insights
    """
    try:
        signals = cleanup_service.get_active_signals_with_ttl()

        if signals is None:
            return {
                "status": "no_active_signals",
                "message": "No active signals available",
                "data": None
            }

        # Extract summary data
        summary_data = {
            "analysis_metadata": signals.get("analysis_metadata", {}),
            "summary": signals.get("summary", {}),
            "total_articles": len(signals.get("news_articles", [])),
            "timestamp": datetime.utcnow().isoformat()
        }

        return {
            "status": "success",
            "data": summary_data
        }

    except Exception as e:
        logger.error(f"Error getting signals summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/by-market")
async def get_signals_by_market(
    market: str = Query(..., description="Market name (e.g., US, India, Crypto, Forex, Global)"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get active signals filtered by market.

    Args:
        market: Market name to filter by

    Requires:
        X-API-Key header with valid API key

    Returns:
        Signals for specified market
    """
    try:
        signals = cleanup_service.get_active_signals_with_ttl()

        if signals is None:
            return {
                "status": "no_active_signals",
                "message": "No active signals available",
                "data": None
            }

        # Filter signals by market
        filtered_articles = []
        for article in signals.get("news_articles", []):
            filtered_signals = [
                s for s in article.get("trading_signals", [])
                if s.get("market", "").upper() == market.upper()
            ]

            if filtered_signals:
                article_copy = article.copy()
                article_copy["trading_signals"] = filtered_signals
                filtered_articles.append(article_copy)

        return {
            "status": "success",
            "market": market,
            "data": {
                "analysis_metadata": signals.get("analysis_metadata", {}),
                "news_articles": filtered_articles,
                "count": sum(len(a.get("trading_signals", [])) for a in filtered_articles)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error filtering signals by market: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/by-exchange")
async def get_signals_by_exchange(
    exchange: str = Query(..., description="Exchange name (e.g., NYSE, NASDAQ, NSE, BSE)"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get active signals filtered by exchange.

    Args:
        exchange: Exchange name to filter by

    Requires:
        X-API-Key header with valid API key

    Returns:
        Signals for specified exchange
    """
    try:
        signals = cleanup_service.get_active_signals_with_ttl()

        if signals is None:
            return {
                "status": "no_active_signals",
                "message": "No active signals available",
                "data": None
            }

        # Filter signals by exchange
        filtered_articles = []
        for article in signals.get("news_articles", []):
            filtered_signals = [
                s for s in article.get("trading_signals", [])
                if s.get("exchange", "").upper() == exchange.upper()
            ]

            if filtered_signals:
                article_copy = article.copy()
                article_copy["trading_signals"] = filtered_signals
                filtered_articles.append(article_copy)

        return {
            "status": "success",
            "exchange": exchange,
            "data": {
                "analysis_metadata": signals.get("analysis_metadata", {}),
                "news_articles": filtered_articles,
                "count": sum(len(a.get("trading_signals", [])) for a in filtered_articles)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error filtering signals by exchange: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/by-signal-type")
async def get_signals_by_type(
    signal_type: str = Query(..., description="Signal type: BUY, SELL, or HOLD"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get active signals filtered by signal type.

    Args:
        signal_type: Signal type to filter by (BUY, SELL, HOLD)

    Requires:
        X-API-Key header with valid API key

    Returns:
        Signals of specified type
    """
    try:
        signal_type = signal_type.upper()
        if signal_type not in ["BUY", "SELL", "HOLD"]:
            raise HTTPException(status_code=400, detail="Invalid signal type. Must be BUY, SELL, or HOLD")

        signals = cleanup_service.get_active_signals_with_ttl()

        if signals is None:
            return {
                "status": "no_active_signals",
                "message": "No active signals available",
                "data": None
            }

        # Filter signals by type
        filtered_articles = []
        for article in signals.get("news_articles", []):
            filtered_signals = [
                s for s in article.get("trading_signals", [])
                if s.get("signal", "") == signal_type
            ]

            if filtered_signals:
                article_copy = article.copy()
                article_copy["trading_signals"] = filtered_signals
                filtered_articles.append(article_copy)

        return {
            "status": "success",
            "signal_type": signal_type,
            "data": {
                "analysis_metadata": signals.get("analysis_metadata", {}),
                "news_articles": filtered_articles,
                "count": sum(len(a.get("trading_signals", [])) for a in filtered_articles)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error filtering signals by type: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/backups")
async def list_backup_dates(api_key: str = Depends(verify_api_key)):
    """
    List all available backup dates.

    Requires:
        X-API-Key header with valid API key

    Returns:
        List of dates with available backups
    """
    try:
        backup_files = cleanup_service.get_backup_files()

        # Extract unique dates
        dates = set()
        for backup_file in backup_files:
            date = backup_file.parent.name
            dates.add(date)

        dates_list = sorted(list(dates), reverse=True)

        return {
            "status": "success",
            "data": {
                "available_dates": dates_list,
                "total_backups": len(backup_files)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error listing backup dates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/signals/history")
async def get_historical_signals(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    api_key: str = Depends(verify_api_key)
):
    """
    Get historical archived signals.

    Args:
        date: Optional date to filter by (YYYY-MM-DD format)
        limit: Maximum number of results to return (1-100)

    Requires:
        X-API-Key header with valid API key

    Returns:
        List of archived signal analyses
    """
    try:
        backup_files = cleanup_service.get_backup_files(date=date)

        if not backup_files:
            return {
                "status": "no_backups",
                "message": f"No backups found{f' for date {date}' if date else ''}",
                "data": []
            }

        # Load backups (limit results)
        backups = []
        for backup_file in backup_files[:limit]:
            backup_data = cleanup_service.load_backup(backup_file)
            if backup_data:
                backups.append(backup_data.model_dump(mode='json'))

        return {
            "status": "success",
            "data": backups,
            "count": len(backups),
            "total_available": len(backup_files),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting historical signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_statistics(api_key: str = Depends(verify_api_key)):
    """
    Get overall statistics about signals and backups.

    Requires:
        X-API-Key header with valid API key

    Returns:
        Statistics about active signals, backups, and system status
    """
    try:
        # Get active signals
        active_signals = cleanup_service.get_active_signals_with_ttl()

        # Get backup info
        backup_files = cleanup_service.get_backup_files()
        backup_dates = set()
        for backup_file in backup_files:
            backup_dates.add(backup_file.parent.name)

        stats = {
            "active_signals": {
                "available": active_signals is not None,
                "count": 0,
                "time_remaining_minutes": 0
            },
            "backups": {
                "total_files": len(backup_files),
                "total_dates": len(backup_dates),
                "oldest_date": min(backup_dates) if backup_dates else None,
                "newest_date": max(backup_dates) if backup_dates else None
            },
            "system": {
                "ttl_minutes": settings.signal_ttl_minutes,
                "cleanup_interval_minutes": settings.cleanup_interval_minutes,
                "news_fetch_interval_minutes": settings.news_fetch_interval_minutes
            }
        }

        if active_signals:
            stats["active_signals"]["count"] = len(active_signals.get("news_articles", []))
            stats["active_signals"]["time_remaining_minutes"] = active_signals.get(
                "analysis_metadata", {}
            ).get("time_remaining_minutes", 0)

        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting NewsTrader API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
