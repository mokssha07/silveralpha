import json
from pathlib import Path
from datetime import datetime

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"

if not mem_path.exists():
    print("No memory available")
    exit()

memory = json.load(open(mem_path))

stats = {}

for r in memory:
    if "label" not in r or "timestamp" not in r:
        continue

    for cid in r.get("active_clusters", []):
        stats.setdefault(cid, []).append({
            "timestamp": r["timestamp"],
            "label": r["label"]
        })

lead_lag = {}

for cid, events in stats.items():
    positives = [e for e in events if e["label"] == 1]
    if not positives:
        continue

    times = [
        datetime.fromisoformat(e["timestamp"])
        for e in positives
    ]

    deltas = [
        (times[i] - times[i - 1]).total_seconds()
        for i in range(1, len(times))
    ]

    if deltas:
        lead_lag[cid] = round(sum(deltas) / len(deltas) / 3600, 2)

out = snap / "lead_lag_stats.json"
json.dump(lead_lag, open(out, "w"), indent=2)

print("Lead-lag statistics updated")
