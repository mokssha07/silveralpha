import json
import requests
from pathlib import Path
from datetime import datetime
from newsplease import NewsPlease

def fetch_historical_news(date_str):
    """
    Fetch silver news from web archive for specific date
    date_str format: '2024-01-15'
    """
    
    sources = [
        f"https://www.kitco.com/news/silver/",
        f"https://www.mining.com/web/tag/silver/",
        f"https://www.ft.com/commodities"
    ]
    
    articles = []
    
    for url in sources:
        try:
            article = NewsPlease.from_url(url)
            if article and article.maintext:
                articles.append({
                    'title': article.title or '',
                    'description': article.maintext[:500] or '',
                    'url': url,
                    'source': article.source_domain or 'web',
                    'date': date_str
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue
    
    return articles

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        date_str = sys.argv[1]
    
    print(f"Fetching news for {date_str}")
    articles = fetch_historical_news(date_str)
    
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_file = out_dir / f"web_{date_str}.json"
    with open(out_file, 'w') as f:
        json.dump(articles, f, indent=2)
    
    print(f"Saved {len(articles)} articles")