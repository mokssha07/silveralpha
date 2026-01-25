import json
from pathlib import Path

snap = Path("data/snapshots")

market = json.load(open(sorted(snap.glob("market_index_*.json"))[-1]))
confidence = json.load(open(sorted(snap.glob("confidence_adj_*.json"))[-1]))

clusters = market["clusters"]
clusters = sorted(clusters, key=lambda x: abs(x["pressure"]), reverse=True)

print("\n=== Prediction Explanation ===")
print(f"Market Pressure Index: {market['market_pressure_index']}")

for c in clusters[:3]:
    cid = c["cluster_id"]
    conf = next(x["confidence"] for x in confidence if x["cluster_id"] == cid)
    print(
        f"- Narrative {cid}: "
        f"pressure={round(c['pressure'],3)}, "
        f"confidence={round(conf,3)}"
    )
