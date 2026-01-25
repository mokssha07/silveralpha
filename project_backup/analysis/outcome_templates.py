import json
from pathlib import Path

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"

if not mem_path.exists():
    print("No memory available")
    exit()

memory = json.load(open(mem_path))

templates = {}

for r in memory:
    if "label" not in r:
        continue

    key = (
        round(r.get("market_pressure_index", 0), 2),
        round(r.get("num_narratives", 0), 1)
    )

    templates.setdefault(str(key), {"count": 0, "success": 0})
    templates[str(key)]["count"] += 1
    if r["label"] == 1:
        templates[str(key)]["success"] += 1

out = snap / "outcome_templates.json"
json.dump(templates, open(out, "w"), indent=2)

print("Outcome templates updated")
