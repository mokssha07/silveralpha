import json
from pathlib import Path

snap = Path("data/snapshots")


def load_latest(pattern, default):
    files = sorted(snap.glob(pattern))
    if not files:
        return default
    return json.load(open(files[-1]))


report = {
    "market": load_latest(
        "market_index_*.json",
        {"market_pressure_index": 0.0, "clusters": []}
    ),
    "confidence": load_latest(
        "confidence_adj_*.json",
        {"confidence": 0.5}
    ),
    "regime": load_latest(
        "regime.json",
        {"regime": "quiet"}
    ),
    "signal_trust": load_latest(
        "regime_trust.json",
        {"signal_trust": 0.5}
    ),
    "conflict": load_latest(
        "narrative_conflict.json",
        {"conflict": False}
    ),
    "multi_horizon": load_latest(
        "multi_horizon.json",
        {"short_term": 0.0, "medium_term": 0.0, "long_term": 0.0}
    )
}

out_path = snap / "final_report.json"
json.dump(report, open(out_path, "w"), indent=2)

print("Final report generated")