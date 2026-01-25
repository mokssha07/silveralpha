import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import sys

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BASE_URLS = [
    "https://finance.yahoo.com/topic/commodities/",
    "https://finance.yahoo.com/topic/markets/",
    "https://finance.yahoo.com/topic/economic-news/",
]

def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")
    items = []

    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = a.get_text(strip=True)
        if "/news/" in href and len(title) > 20:
            items.append({
                "source": "Yahoo Finance",
                "title": title,
                "summary": title,
                "published": ""
            })
    return items

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ingest_yahoo.py YYYY-MM-DD")
        sys.exit(1)

    run_date = sys.argv[1]
    all_docs = []

    for url in BASE_URLS:
        all_docs.extend(fetch_page(url))

    ts = datetime.fromisoformat(run_date).strftime("%Y-%m-%d")
    out = OUT_DIR / f"yahoo_snapshot_{ts}.json"

    with open(out, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2)

    print(f"Saved {len(all_docs)} historical articles")