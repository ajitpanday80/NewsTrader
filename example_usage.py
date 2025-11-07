"""
Example usage of NewsTrader components.
Demonstrates how to use individual modules.
"""

import json
from src.news_fetcher import news_fetcher
from src.signal_generator import signal_generator
from src.cleanup_service import cleanup_service


def example_fetch_news():
    """Example: Fetch latest news from Alpha Vantage."""
    print("=" * 80)
    print("Example 1: Fetching Latest News")
    print("=" * 80)

    # Fetch latest 10 articles
    articles = news_fetcher.get_latest_articles(limit=10)

    print(f"\nFetched {len(articles)} articles:\n")

    for idx, article in enumerate(articles, 1):
        print(f"{idx}. {article['title']}")
        print(f"   Source: {article['source']}")
        print(f"   Sentiment: {article['overall_sentiment_label']} ({article['overall_sentiment_score']})")
        print(f"   Tickers mentioned: {len(article['ticker_sentiment'])}")
        if article.get('url'):
            print(f"   URL: {article['url']}")
        print()


def example_fetch_by_topics():
    """Example: Fetch news filtered by topics."""
    print("=" * 80)
    print("Example 2: Fetching News by Topics")
    print("=" * 80)

    # Fetch news about earnings and IPOs
    topics = ["earnings", "ipo"]
    articles = news_fetcher.fetch_news_by_topics(topics, limit=5)

    print(f"\nFetched {len(articles.get('feed', []))} articles about {', '.join(topics)}:\n")

    for idx, article in enumerate(articles.get('feed', []), 1):
        parsed = news_fetcher.parse_news_article(article)
        print(f"{idx}. {parsed['title']}")
        print(f"   Topics: {', '.join(parsed['topics'])}")
        print()


def example_generate_signals():
    """Example: Generate trading signals from news."""
    print("=" * 80)
    print("Example 3: Generating Trading Signals")
    print("=" * 80)

    # Fetch news
    print("\nFetching news...")
    articles = news_fetcher.get_latest_articles(limit=5)

    if not articles:
        print("No articles fetched. Check your API key.")
        return

    # Generate signals
    print(f"Analyzing {len(articles)} articles with Groq AI...")
    result = signal_generator.generate_signals(articles)

    # Display results
    print(f"\n✓ Analysis Complete!")
    print(f"  - Analysis ID: {result.analysis_metadata.analysis_id}")
    print(f"  - Articles analyzed: {result.analysis_metadata.total_articles_analyzed}")
    print(f"  - Signals generated: {result.analysis_metadata.total_signals_generated}")
    print(f"  - Markets covered: {', '.join(result.analysis_metadata.markets_covered)}")
    print(f"  - Expires at: {result.analysis_metadata.expires_at}")
    print()

    # Show some signals
    print("Sample Trading Signals:")
    print("-" * 80)

    signal_count = 0
    for article in result.news_articles:
        for signal in article.trading_signals[:3]:  # Show first 3 signals
            signal_count += 1
            print(f"\n{signal_count}. {signal.signal.value} {signal.ticker} ({signal.name})")
            print(f"   Exchange: {signal.exchange} | Market: {signal.market}")
            print(f"   Confidence: {signal.confidence:.2f} | Strength: {signal.strength}")
            print(f"   Timeframe: {signal.timeframe} | Entry: {signal.entry_strategy}")
            print(f"   Reasoning: {signal.reasoning[:150]}...")
            print(f"   Risk Factors: {', '.join(signal.risk_factors[:2])}")

            if signal_count >= 5:
                break
        if signal_count >= 5:
            break

    print("\n" + "=" * 80)


def example_save_and_load():
    """Example: Save and load signals."""
    print("=" * 80)
    print("Example 4: Save and Load Signals")
    print("=" * 80)

    # Fetch and generate
    articles = news_fetcher.get_latest_articles(limit=3)

    if not articles:
        print("No articles to analyze")
        return

    result = signal_generator.generate_signals(articles)

    # Save
    print("\nSaving signals...")
    cleanup_service.save_active_signals(result)
    print("✓ Signals saved to data/active/current_signals.json")

    # Load
    print("\nLoading signals...")
    loaded_result = cleanup_service.load_active_signals()

    if loaded_result:
        print(f"✓ Loaded signals for analysis: {loaded_result.analysis_metadata.analysis_id}")
        print(f"  Total signals: {loaded_result.analysis_metadata.total_signals_generated}")

        # Check expiry
        time_remaining = cleanup_service.get_time_remaining(loaded_result)
        print(f"  Time remaining: {time_remaining} minutes")

    print("\n" + "=" * 80)


def example_json_output():
    """Example: Generate and export JSON."""
    print("=" * 80)
    print("Example 5: JSON Output for Website")
    print("=" * 80)

    # Generate signals
    articles = news_fetcher.get_latest_articles(limit=2)

    if not articles:
        print("No articles to analyze")
        return

    result = signal_generator.generate_signals(articles)

    # Convert to JSON
    json_data = result.model_dump(mode='json')

    # Save to file
    output_file = "example_output.json"
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)

    print(f"\n✓ JSON output saved to {output_file}")
    print(f"\nJSON structure:")
    print(f"  - analysis_metadata: {len(json_data['analysis_metadata'])} fields")
    print(f"  - news_articles: {len(json_data['news_articles'])} articles")
    print(f"  - summary: {len(json_data['summary'])} fields")

    # Show sample
    print(f"\nSample metadata:")
    print(json.dumps(json_data['analysis_metadata'], indent=2, default=str)[:500] + "...")

    print("\n" + "=" * 80)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "NewsTrader Example Usage" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    try:
        # Run examples
        example_fetch_news()
        input("\nPress Enter to continue to next example...")

        example_fetch_by_topics()
        input("\nPress Enter to continue to next example...")

        example_generate_signals()
        input("\nPress Enter to continue to next example...")

        example_save_and_load()
        input("\nPress Enter to continue to next example...")

        example_json_output()

        print("\n✓ All examples completed!")
        print("\nTo run the full system:")
        print("  python -m src.main --api")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have:")
        print("  1. Configured .env file with API keys")
        print("  2. Installed all requirements: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
