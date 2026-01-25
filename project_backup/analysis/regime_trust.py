import json
from pathlib import Path

snap = Path("data/snapshots")

state_files = (
    sorted(snap.glob("regime_state.json")) or
    sorted(snap.glob("regime.json"))
)

out_path = snap / "regime_trust.json"

if not state_files:
    trust = {
        "signal_trust": 0.5,
        "reason": "neutral_fallback"
    }
    json.dump(trust, open(out_path, "w"), indent=2)
    print("Neutral regime trust written")
    exit()

state = json.load(open(state_files[-1]))
regime = state.get("regime", "neutral")

if regime == "momentum":
    signal_trust = 0.8
elif regime == "trending":
    signal_trust = 0.65
elif regime == "quiet":
    signal_trust = 0.4
else:
    signal_trust = 0.5

trust = {
    "signal_trust": signal_trust,
    "regime": regime
}

json.dump(trust, open(out_path, "w"), indent=2)
print(f"Signal trust set to {signal_trust} for regime {regime}")