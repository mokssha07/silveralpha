import json
from pathlib import Path

snap = Path("data/snapshots")

pressure_files = sorted(
    [path for path in snap.glob("final_pressure_*.json") if not path.stem.endswith("_latest")] or list(snap.glob("final_pressure_*.json")),
    key=lambda path: path.stat().st_mtime
)
out_path = snap / "narrative_conflict.json"

if not pressure_files:
    neutral = {
        "conflict": False,
        "reason": "no_pressure_data"
    }
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("No narrative conflict (no pressure data)")
    exit()

pressure = json.load(open(pressure_files[-1]))

bullish = sum(1 for c in pressure if c.get("direction") in ("Bullish", "up") or c.get("final_pressure", 0) > 0)
bearish = sum(1 for c in pressure if c.get("direction") in ("Bearish", "down") or c.get("final_pressure", 0) < 0)

conflict = bullish > 0 and bearish > 0

result = {
    "conflict": conflict,
    "bullish_count": bullish,
    "bearish_count": bearish
}

json.dump(result, open(out_path, "w"), indent=2)
print("Narrative conflict assessed")
