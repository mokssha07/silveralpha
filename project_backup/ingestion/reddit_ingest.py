"""
Reddit ingestion with HARD filtering.
Reddit is treated as signal confirmation, not narrative discovery.
"""

import praw
import json
from pathlib import Path
from datetime import datetime



ALLOWED_SUBREDDITS = [
    "Silverbugs",
    "commodities",
    "wallstreetbetsOGs",
    "MacroAnalysis"
]

MIN_WORD_COUNT = 120
MIN_UPVOTES = 15
BLOCKED_KEYWORDS = [
    "moon", "yolo", "pump", "dump", "to the moon",
    "price target", "buy now", "sell", "call", "put",
    "meme", "🚀"
]

DATA_DIR = Path("data/reddit")
DATA_DIR.mkdir(parents=True, exist_ok=True)



reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="silveralpha_intel_bot"
)


def is_valid_post(post):
    text = (post.title + " " + (post.selftext or "")).lower()

    if len(text.split()) < MIN_WORD_COUNT:
        return False

    if post.score < MIN_UPVOTES:
        return False

    for kw in BLOCKED_KEYWORDS:
        if kw in text:
            return False

    return True


def ingest():
    collected = []

    for sub in ALLOWED_SUBREDDITS:
        subreddit = reddit.subreddit(sub)

        for post in subreddit.hot(limit=50):
            if not is_valid_post(post):
                continue

            collected.append({
                "source": f"reddit/{sub}",
                "title": post.title,
                "text": post.selftext,
                "score": post.score,
                "created_utc": post.created_utc
            })

    if not collected:
        print("Reddit: 0 high-quality posts")
        return

    ts = datetime.utcnow().strftime("%Y-%m-%d_%H-%M")
    out = DATA_DIR / f"reddit_{ts}.json"

    with open(out, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    print(f"Reddit: saved {len(collected)} high-quality posts")


if __name__ == "__main__":
    ingest()
