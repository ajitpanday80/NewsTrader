"""
Main orchestrator for NewsTrader application.
Coordinates news fetching, signal generation, cleanup, and API server.
"""

import sys
import signal as signal_module
import threading
import time
from datetime import datetime
from loguru import logger
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import settings
from src.news_fetcher import news_fetcher
from src.signal_generator import signal_generator
from src.cleanup_service import cleanup_service


class NewsTraderOrchestrator:
    """Main orchestrator for NewsTrader application."""

    def __init__(self):
        """Initialize orchestrator."""
        self.scheduler = BackgroundScheduler()
        self.running = False

        # Configure logging
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=settings.log_level
        )
        logger.add(
            settings.logs_dir / "newstrader_{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}"
        )

    def fetch_and_analyze_news(self):
        """
        Fetch latest news and generate signals.
        This is the main processing job.
        """
        try:
            logger.info("=" * 80)
            logger.info("Starting news fetch and analysis cycle")
            logger.info("=" * 80)

            # Fetch latest news
            logger.info("Fetching latest news from Alpha Vantage...")
            articles = news_fetcher.get_latest_articles(limit=50)

            if not articles:
                logger.warning("No news articles fetched")
                return

            logger.info(f"Fetched {len(articles)} news articles")

            # Log article titles
            for idx, article in enumerate(articles[:5], 1):
                logger.info(f"  {idx}. {article.get('title', 'N/A')}")

            # Generate signals using Groq AI
            logger.info("Generating trading signals with Groq AI...")
            result = signal_generator.generate_signals(articles)

            logger.info(f"Generated {result.analysis_metadata.total_signals_generated} trading signals")
            logger.info(f"Analyzed {result.analysis_metadata.total_articles_analyzed} articles")
            logger.info(f"Markets covered: {', '.join(result.analysis_metadata.markets_covered)}")

            # Save to active signals
            logger.info("Saving signals to active database...")
            cleanup_service.save_active_signals(result)

            logger.info(f"✓ Analysis complete! Signals will expire at {result.analysis_metadata.expires_at}")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Error in fetch_and_analyze_news: {e}", exc_info=True)

    def cleanup_expired(self):
        """
        Check for and cleanup expired signals.
        This job runs periodically to remove old signals.
        """
        try:
            logger.debug("Running cleanup check...")
            cleaned = cleanup_service.cleanup_expired_signals()

            if cleaned:
                logger.info("✓ Expired signals cleaned up and backed up")
            else:
                logger.debug("No cleanup needed")

        except Exception as e:
            logger.error(f"Error in cleanup_expired: {e}", exc_info=True)

    def start(self):
        """Start the orchestrator with scheduled jobs."""
        try:
            logger.info("=" * 80)
            logger.info("NewsTrader Orchestrator Starting")
            logger.info("=" * 80)
            logger.info(f"Signal TTL: {settings.signal_ttl_minutes} minutes")
            logger.info(f"News fetch interval: {settings.news_fetch_interval_minutes} minutes")
            logger.info(f"Cleanup interval: {settings.cleanup_interval_minutes} minutes")
            logger.info("=" * 80)

            # Run initial fetch immediately
            logger.info("Running initial news fetch and analysis...")
            self.fetch_and_analyze_news()

            # Schedule periodic news fetch
            self.scheduler.add_job(
                self.fetch_and_analyze_news,
                trigger=IntervalTrigger(minutes=settings.news_fetch_interval_minutes),
                id="fetch_news",
                name="Fetch News and Generate Signals",
                max_instances=1
            )
            logger.info(f"✓ Scheduled news fetch job (every {settings.news_fetch_interval_minutes} minutes)")

            # Schedule periodic cleanup
            self.scheduler.add_job(
                self.cleanup_expired,
                trigger=IntervalTrigger(minutes=settings.cleanup_interval_minutes),
                id="cleanup",
                name="Cleanup Expired Signals",
                max_instances=1
            )
            logger.info(f"✓ Scheduled cleanup job (every {settings.cleanup_interval_minutes} minutes)")

            # Start scheduler
            self.scheduler.start()
            self.running = True

            logger.info("=" * 80)
            logger.info("✓ NewsTrader Orchestrator Started Successfully")
            logger.info("=" * 80)

            # Keep running
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                self.stop()

        except Exception as e:
            logger.error(f"Error starting orchestrator: {e}", exc_info=True)
            self.stop()

    def stop(self):
        """Stop the orchestrator."""
        try:
            logger.info("Stopping NewsTrader Orchestrator...")

            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("✓ Scheduler stopped")

            self.running = False
            logger.info("✓ NewsTrader Orchestrator stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping orchestrator: {e}", exc_info=True)

    def run_with_api_server(self):
        """
        Run orchestrator alongside the API server.
        The API server runs in a separate thread.
        """
        import uvicorn
        from src.api_server import app

        # Start orchestrator in background thread
        orchestrator_thread = threading.Thread(target=self.start, daemon=True)
        orchestrator_thread.start()

        logger.info(f"Starting API server on {settings.api_host}:{settings.api_port}")

        # Run API server in main thread
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower()
        )


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Received shutdown signal")
    sys.exit(0)


def main():
    """Main entry point."""
    # Set up signal handlers
    signal_module.signal(signal_module.SIGINT, signal_handler)
    signal_module.signal(signal_module.SIGTERM, signal_handler)

    # Create and run orchestrator
    orchestrator = NewsTraderOrchestrator()

    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--api":
        # Run with API server
        orchestrator.run_with_api_server()
    else:
        # Run orchestrator only
        orchestrator.start()


if __name__ == "__main__":
    main()
