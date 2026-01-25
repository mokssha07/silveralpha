import feedparser
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

rss_feeds = {
    "Kitco": "https://www.kitco.com/rss/news",
    "Mining.com": "https://www.mining.com/feed/",
    "Reuters Commodities": "https://www.reuters.com/markets/commodities/rss",
    "Reuters Metals": "https://www.reuters.com/markets/metals/rss",
    "Reuters Macro": "https://www.reuters.com/markets/macroeconomics/rss",
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "Bloomberg Markets": "https://www.bloomberg.com/markets/rss",
    "Financial Times Commodities": "https://www.ft.com/commodities?format=rss",
    "IEA Energy": "https://www.iea.org/rss/news.xml",
    "World Bank Commodities": "https://www.worldbank.org/en/news/all?format=rss",
}

if len(sys.argv) > 1:
    RUN_DATE = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
else:
    RUN_DATE = datetime.now(timezone.utc)

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)


def ingest_rss():
    docs = []

    for source, url in rss_feeds.items():
        feed = feedparser.parse(
            url,
            request_headers={"User-Agent": "Mozilla/5.0"}
        )

        print(f"{source}: {len(feed.entries)} entries")

        for entry in feed.entries:
            if not hasattr(entry, "published_parsed"):
                continue

            try:
                published_dt = datetime(
                    *entry.published_parsed[:6],
                    tzinfo=timezone.utc
                )
            except:
                continue

            if published_dt > RUN_DATE:
                continue

            docs.append({
                "source": source,
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "published": published_dt.isoformat()
            })

    return docs


def save_snapshot(docs):
    timestamp = RUN_DATE.strftime("%Y-%m-%d_%H-%M")
    filename = f"rss_snapshot_{timestamp}.json"

    with open(output_dir / filename, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(docs)} articles")


if __name__ == "__main__":
    documents = ingest_rss()
    save_snapshot(documents)