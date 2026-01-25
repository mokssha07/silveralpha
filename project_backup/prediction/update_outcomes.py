import json
from pathlib import Path

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"
regime_path = snap / "regime_state.json"

if not mem_path.exists():
    print("No memory found")
    exit()

memory = json.load(open(mem_path))

ACTUAL_RETURN = float(input("Enter realized price return: "))
THRESHOLD = 0.01

outcome = 1 if abs(ACTUAL_RETURN) > THRESHOLD else 0

memory[-1]["realized_return"] = ACTUAL_RETURN
memory[-1]["label"] = outcome

if regime_path.exists():
    memory[-1]["regime"] = json.load(open(regime_path))["regime"]

json.dump(memory, open(mem_path, "w"), indent=2)
print("Outcome recorded")
