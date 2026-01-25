import json
from pathlib import Path

snap = Path("data/snapshots")

base_files = sorted(snap.glob("confidence_*.json"))

out_path = snap / "confidence_adj_neutral.json"

if not base_files:
    neutral = {
        "confidence": 0.5,
        "source": "neutral_fallback"
    }
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("Neutral adjusted confidence written (no base confidence)")
    exit()

base = json.load(open(base_files[-1]))

adjusted = {
    "confidence": base.get("confidence", 0.5),
    "source": "no_reddit_confirmation"
}

json.dump(adjusted, open(out_path, "w"), indent=2)
print("Neutral adjusted confidence written (no reddit confirmation)")