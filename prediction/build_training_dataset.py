import argparse
import json
from datetime import datetime
from pathlib import Path


SNAP = Path("data/snapshots")
PRICE_FILE = Path("data/prices/silver_daily.json")
OUT_FILE = SNAP / "training_dataset.json"


def parse_snapshot_date(path):
    stem = path.stem
    for prefix in ("market_index_", "clusters_"):
        if stem.startswith(prefix):
            raw = stem.replace(prefix, "")
            if raw == "latest":
                return None
            for fmt in ("%Y-%m-%d_%H-%M", "%Y-%m-%d"):
                try:
                    return datetime.strptime(raw, fmt).date().isoformat()
                except ValueError:
                    pass
    return None


def pressure(cluster):
    return cluster.get("final_pressure", cluster.get("pressure", 0.0))


def load_prices(horizon):
    if not PRICE_FILE.exists():
        raise FileNotFoundError(f"Missing {PRICE_FILE}. Run data/prices/fetch_silver_prices.py first.")
    payload = json.load(open(PRICE_FILE, encoding="utf-8"))
    by_date = {}
    for row in payload.get("rows", []):
        returns = row.get("forward_returns", {})
        if str(horizon) in returns:
            by_date[row["date"]] = returns[str(horizon)]
    return by_date


def nearest_return(price_by_date, date):
    if date in price_by_date:
        return price_by_date[date]
    dates = sorted(d for d in price_by_date if d >= date)
    if dates:
        return price_by_date[dates[0]]
    return None


def features_from_market(path):
    market = json.load(open(path, encoding="utf-8"))
    clusters = market.get("clusters", [])
    pressures = [pressure(c) for c in clusters]
    abs_pressures = [abs(p) for p in pressures]
    total = sum(abs_pressures)
    signed = sum(pressures)
    return {
        "market_pressure_index": signed / total if total else market.get("market_pressure_index", 0.0),
        "num_narratives": len(clusters),
        "max_cluster_pressure": max(abs_pressures, default=0.0),
        "mean_cluster_pressure": signed / len(clusters) if clusters else 0.0,
        "bullish_share": sum(1 for p in pressures if p > 0) / len(clusters) if clusters else 0.0,
        "bearish_share": sum(1 for p in pressures if p < 0) / len(clusters) if clusters else 0.0,
        "mean_confidence": 0.5,
    }


def features_from_clusters(path):
    clusters = json.load(open(path, encoding="utf-8"))
    if not any(c.get("documents") or c.get("sources") for c in clusters):
        return None
    pressures = [pressure(c) for c in clusters]
    abs_pressures = [abs(p) for p in pressures]
    total = sum(abs_pressures)
    signed = sum(pressures)
    stabilities = [c.get("stability", 0.0) for c in clusters]
    return {
        "market_pressure_index": signed / total if total else 0.0,
        "num_narratives": len(clusters),
        "max_cluster_pressure": max(abs_pressures, default=0.0),
        "mean_cluster_pressure": signed / len(clusters) if clusters else 0.0,
        "bullish_share": sum(1 for p in pressures if p > 0) / len(clusters) if clusters else 0.0,
        "bearish_share": sum(1 for p in pressures if p < 0) / len(clusters) if clusters else 0.0,
        "mean_confidence": sum(stabilities) / len(stabilities) if stabilities else 0.5,
    }


def snapshot_feature_rows():
    rows = []
    market_files = sorted(SNAP.glob("market_index_*.json"))
    cluster_files = sorted(SNAP.glob("clusters_*.json"))
    valid_cluster_dates = set()

    for path in cluster_files:
        date = parse_snapshot_date(path)
        features = features_from_clusters(path) if date else None
        if features:
            valid_cluster_dates.add(date)

    for path in market_files:
        date = parse_snapshot_date(path)
        if date and date in valid_cluster_dates:
            rows.append({"date": date, **features_from_market(path), "source_file": str(path)})

    market_dates = {row["date"] for row in rows}
    for path in cluster_files:
        date = parse_snapshot_date(path)
        if date and date not in market_dates:
            features = features_from_clusters(path)
            if features:
                rows.append({"date": date, **features, "source_file": str(path)})

    return sorted(rows, key=lambda row: row["date"])


def main():
    parser = argparse.ArgumentParser(description="Join narrative snapshots to future silver returns.")
    parser.add_argument("--horizon", type=int, default=5, help="Forward return horizon in trading days.")
    parser.add_argument("--threshold", type=float, default=0.02, help="Absolute return threshold for label=1.")
    args = parser.parse_args()

    price_by_date = load_prices(args.horizon)
    examples = []

    for row in snapshot_feature_rows():
        future_return = nearest_return(price_by_date, row["date"])
        if future_return is None:
            continue
        examples.append({
            **row,
            "horizon_days": args.horizon,
            "future_return": future_return,
            "abs_future_return": abs(future_return),
            "label": 1 if abs(future_return) >= args.threshold else 0,
            "label_threshold": args.threshold,
        })

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "horizon_days": args.horizon,
            "label_threshold": args.threshold,
            "num_examples": len(examples),
            "examples": examples,
        }, f, indent=2)

    positives = sum(row["label"] for row in examples)
    print(f"Saved {len(examples)} training examples to {OUT_FILE} ({positives} positive)")


if __name__ == "__main__":
    main()
