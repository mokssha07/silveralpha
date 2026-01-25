import json
from pathlib import Path

snap = Path("data/snapshots")

mem = json.load(open(snap / "prediction_memory.json"))
latest = mem[-1]

trust = 0.5
if (snap / "regime_trust.json").exists():
    trust = json.load(open(snap / "regime_trust.json"))["signal_trust"]

conflict = False
if (snap / "narrative_conflict.json").exists():
    conflict = json.load(open(snap / "narrative_conflict.json"))["conflict"]

proba = latest.get("predicted_proba", 0.5)

if conflict or trust < 0.4:
    action = "IGNORE"
elif proba > 0.65 and trust > 0.7:
    action = "ACT"
else:
    action = "WATCH"

out = {
    "action": action,
    "predicted_proba": proba,
    "signal_trust": trust,
    "conflict": conflict
}

json.dump(out, open(snap / "action_state.json", "w"), indent=2)
print(f"Action state: {action}")
