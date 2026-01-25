import requests
import json
from pathlib import Path
from datetime import datetime
import feedparser
import time

def get_wayback_snapshot(url, date_str):
    """
    Get historical RSS snapshot from Wayback Machine
    date_str format: '20240115' (YYYYMMDD)
    """
    wayback_url = f"https://web.archive.org/web/{date_str}/{url}"
    
    try:
        response = requests.get(wayback_url, timeout=30)
        if response.status_code == 200:
            feed = feedparser.parse(response.content)
            return feed.entries
        else:
            print(f"No snapshot found for {url} on {date_str}")
            return []
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def fetch_historical_news(date_str):
    """
    date_str format: '2024-01-15'
    """
    wayback_date = datetime.strptime(date_str, '%Y-%m-%d').strftime('%Y%m%d')
    
    rss_feeds = {
        "Kitco": "https://www.kitco.com/rss/",
        "Mining.com": "https://www.mining.com/feed/",
        "Reuters": "https://www.reuters.com/rssFeed/businessNews",
    }
    
    all_articles = []
    
    for source, url in rss_feeds.items():
        print(f"Fetching {source} from {date_str}...")
        entries = get_wayback_snapshot(url, wayback_date)
        
        for entry in entries[:20]:
            article = {
                'title': entry.get('title', ''),
                'description': entry.get('summary', ''),
                'url': entry.get('link', ''),
                'source': source,
                'date': date_str
            }
            all_articles.append(article)
        
        time.sleep(2)
    
    return all_articles

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        date_str = sys.argv[1]
    
    print(f"Fetching historical news for {date_str}")
    articles = fetch_historical_news(date_str)
    
    out_dir = Path("data/raw")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    all_content = []
    for article in articles:
        all_content.append({
            'text': f"{article['title']} {article['description']}",
            'source': article['source'],
            'date': article['date']
        })
    
    out_file = out_dir / "articles.json"
    with open(out_file, 'w') as f:
        json.dump(all_content, f, indent=2)
    
    print(f"Saved {len(all_content)} articles")