import csv
import json
import requests
from io import StringIO

URL = "https://stooq.com/q/d/l/?s=xagusd&i=d"

r = requests.get(URL)
r.raise_for_status()

csv_data = StringIO(r.text)
reader = csv.reader(csv_data)

next(reader)

prices = {}
for row in reader:
    if len(row) < 5:
        continue
    date, close = row[0], row[4]
    if close:
        prices[date] = float(close)

with open("data/prices/silver_daily.json", "w") as f:
    json.dump(prices, f, indent=2)

print(f"Saved {len(prices)} daily prices")