import feedparser
import json
import sys
import os
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

reddit_subreddits = [
    "silverbugs",
    "investing",
    "stocks",
    "commodities",
    "mining"
]

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


def ingest_reddit():
    """
    Ingest silver/metals related content from Reddit subreddits.
    Returns list of documents with source, title, summary, published, upvotes.
    Gracefully handles missing credentials or API errors.
    """
    docs = []
    
    try:
        import praw
    except ImportError:
        print("Reddit integration: praw not installed, skipping Reddit data")
        return docs
    
    # Check for Reddit API credentials
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Reddit integration: REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET not set, skipping Reddit data")
        return docs
    
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="silveralpha/1.0 (narrative intelligence)"
        )
        
        for subreddit_name in reddit_subreddits:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                print(f"Reddit/{subreddit_name}: fetching posts...")
                
                # Fetch hot posts (recent and popular)
                for post in subreddit.hot(limit=50):
                    try:
                        docs.append({
                            "source": f"Reddit/{subreddit_name}",
                            "title": post.title,
                            "summary": post.selftext[:500] if post.selftext else f"[Link: {post.url}]",
                            "published": datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                            "upvotes": post.score,
                            "url": f"https://reddit.com{post.permalink}"
                        })
                    except Exception as post_err:
                        continue
                
                # Fetch top comments from top posts (condensed for volume)
                try:
                    for post in subreddit.hot(limit=10):
                        post.comments.replace_more(limit=0)  # Flatten comment tree
                        for comment in post.comments[:10]:  # Top 10 comments per post
                            if comment.score > 5:  # Only significant comments
                                docs.append({
                                    "source": f"Reddit/{subreddit_name}/comment",
                                    "title": "[Comment] " + post.title[:50],
                                    "summary": comment.body[:500],
                                    "published": datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).isoformat(),
                                    "upvotes": comment.score,
                                    "url": f"https://reddit.com{comment.permalink}"
                                })
                except Exception:
                    pass  # Some posts might not allow comment access
                    
            except Exception as sub_err:
                print(f"Reddit/{subreddit_name}: error fetching - {sub_err}")
                continue
        
        print(f"Reddit: fetched {len(docs)} posts/comments")
        
    except Exception as err:
        print(f"Reddit integration error: {err}")
    
    return docs


def save_snapshot(docs):
    timestamp = RUN_DATE.strftime("%Y-%m-%d_%H-%M")
    filename = f"rss_snapshot_{timestamp}.json"

    with open(output_dir / filename, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(docs)} articles")


if __name__ == "__main__":
    documents = ingest_rss()
    reddit_docs = ingest_reddit()
    documents.extend(reddit_docs)
    save_snapshot(documents)