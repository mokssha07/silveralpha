import json
from pathlib import Path

snap = Path("data/snapshots")

mem_path = snap / "prediction_memory.json"
action_path = snap / "action_state.json"
regime_path = snap / "regime_state.json"
conflict_path = snap / "narrative_conflict.json"

if not mem_path.exists():
    print("No memory found")
    exit()

memory = json.load(open(mem_path))
latest = memory[-1]

if "label" not in latest or "predicted_proba" not in latest:
    print("Outcome or prediction missing")
    exit()

predicted = latest["predicted_proba"]
actual = latest["label"]

if (predicted >= 0.5) == actual:
    print("Prediction correct — no failure logged")
    exit()

reasons = []

if regime_path.exists():
    regime = json.load(open(regime_path))["regime"]
    if regime in ["noisy", "transition"]:
        reasons.append("unreliable_regime")

if conflict_path.exists():
    if json.load(open(conflict_path))["conflict"]:
        reasons.append("narrative_conflict")

if predicted < 0.55:
    reasons.append("weak_signal")

if not reasons:
    reasons.append("unexpected_event")

latest["failure_reasons"] = reasons

json.dump(memory, open(mem_path, "w"), indent=2)
print("Failure reasons logged:", reasons)
