import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


OUT_DIR = Path("data/prices")
OUT_FILE = OUT_DIR / "silver_daily.json"
RETURNS_FILE = Path("data/price_returns.json")


def to_unix(date_str):
    dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def fetch_yahoo(symbol, start_date, end_date):
    period1 = to_unix(start_date)
    period2 = to_unix(end_date) + 86400
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": period1,
        "period2": period2,
        "interval": "1d",
        "events": "history",
        "includeAdjustedClose": "true",
    }
    response = requests.get(url, params=params, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    payload = response.json()
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    adjclose = result["indicators"].get("adjclose", [{}])[0].get("adjclose", [])

    rows = []
    for i, ts in enumerate(timestamps):
        close = adjclose[i] if i < len(adjclose) and adjclose[i] is not None else quote["close"][i]
        if close is None:
            continue
        rows.append({
            "date": datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d"),
            "open": quote["open"][i],
            "high": quote["high"][i],
            "low": quote["low"][i],
            "close": close,
            "volume": quote["volume"][i],
            "symbol": symbol,
            "source": "yahoo_chart",
        })
    return rows


def add_forward_returns(rows, horizons):
    rows = sorted(rows, key=lambda row: row["date"])
    for row in rows:
        row["forward_returns"] = {}

    for i, row in enumerate(rows):
        close = row["close"]
        for horizon in horizons:
            if i + horizon < len(rows) and close:
                future_close = rows[i + horizon]["close"]
                row["forward_returns"][str(horizon)] = round((future_close - close) / close, 6)
    return rows


def main():
    parser = argparse.ArgumentParser(description="Fetch daily silver futures prices for training labels.")
    parser.add_argument("--symbol", default="SI=F", help="Yahoo Finance symbol for silver futures.")
    parser.add_argument("--start", default="2016-05-01")
    parser.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--horizons", default="1,5,10,20", help="Trading-day forward return horizons.")
    args = parser.parse_args()

    horizons = [int(item.strip()) for item in args.horizons.split(",") if item.strip()]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = fetch_yahoo(args.symbol, args.start, args.end)
    rows = add_forward_returns(rows, horizons)

    payload = {
        "symbol": args.symbol,
        "start": args.start,
        "end": args.end,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "rows": rows,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    latest = rows[-1] if rows else {}
    latest_return = latest.get("forward_returns", {}).get(str(horizons[0]), 0.0)
    with open(RETURNS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "latest_return": latest_return,
            "rows": len(rows),
            "source": str(OUT_FILE),
            "updated_at": int(time.time()),
        }, f, indent=2)

    print(f"Saved {len(rows)} silver price rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
