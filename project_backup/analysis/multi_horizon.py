import json
from pathlib import Path

snap = Path("data/snapshots")
velocity_files = sorted(snap.glob("velocity_*.json"))
out_path = snap / "multi_horizon.json"

if not velocity_files:
    neutral = {
        "short_term": 0.0,
        "medium_term": 0.0,
        "long_term": 0.0,
        "reason": "no_velocity_data"
    }
    json.dump(neutral, open(out_path, "w"), indent=2)
    print("Neutral multi-horizon signals written")
    exit()

velocity_list = json.load(open(velocity_files[-1]))

if velocity_list:
    velocities = [c["velocity"] for c in velocity_list]
    avg_velocity = sum(velocities) / len(velocities)
    max_velocity = max(velocities)
    min_velocity = min(velocities)
else:
    avg_velocity = 0.0
    max_velocity = 0.0
    min_velocity = 0.0

result = {
    "short_term": round(max_velocity * 0.1, 2),
    "medium_term": round(avg_velocity * 0.1, 2),
    "long_term": round(min_velocity * 0.1, 2)
}

json.dump(result, open(out_path, "w"), indent=2)
print("Multi-horizon signals derived")