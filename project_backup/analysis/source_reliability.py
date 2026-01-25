import json
from pathlib import Path

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"

if not mem_path.exists():
    print("No memory available")
    exit()

memory = json.load(open(mem_path))

stats = {}

for r in memory:
    if "label" not in r:
        continue
    for src in r.get("sources", []):
        stats.setdefault(src, {"hits": 0, "total": 0})
        stats[src]["total"] += 1
        if r["label"] == 1:
            stats[src]["hits"] += 1

scores = {}
for src, s in stats.items():
    if s["total"] == 0:
        continue
    scores[src] = round(s["hits"] / s["total"], 3)

out = snap / "source_reliability.json"
json.dump(scores, open(out, "w"), indent=2)

print("Source reliability scores updated")
