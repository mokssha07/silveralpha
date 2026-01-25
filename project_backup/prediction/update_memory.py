# READ-ONLY PREDICTION LAYER
# Appends snapshot results to long-term memory

import json
from pathlib import Path

snap = Path("data/snapshots")
mem = snap / "prediction_memory.json"

current = json.load(open(snap / "prediction_labeled.json"))

history = []
if mem.exists():
    history = json.load(open(mem))

history.append(current)

with open(mem, "w") as f:
    json.dump(history, f, indent=2)

print(f"Memory size: {len(history)} snapshots")
