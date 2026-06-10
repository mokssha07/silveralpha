import json
from pathlib import Path
import numpy as np

snap_dir = Path("data/snapshots")

def latest(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} found")
        exit()
    timestamped = [path for path in files if not path.stem.endswith("_latest")]
    if timestamped:
        files = timestamped
    return max(files, key=lambda path: path.stat().st_mtime)

if __name__ == "__main__":
    vel_path = latest("velocity_*.json")
    with open(vel_path, "r", encoding="utf-8") as f:
        velocity_data = json.load(f)
    
    # Load lifecycle data for temporal decay application
    lifecycle_data = {}
    lifecycle_path = snap_dir / "narrative_lifecycle.json"
    if lifecycle_path.exists():
        try:
            lifecycle_list = json.load(open(lifecycle_path))
            lifecycle_data = {item["cluster_id"]: item for item in lifecycle_list}
        except Exception:
            pass
    
    output = []
    for c in velocity_data:
        cluster_id = c["cluster_id"]
        velocity = c.get("velocity", 0)
        size = c.get("size", 0)
        impact = c.get("impact_score", 1)
        stability = c.get("stability", 1)
        
        # A2: Apply temporal decay - recent velocity matters more
        # Narratives persist better if they keep showing up
        lifecycle = lifecycle_data.get(cluster_id, {})
        state = lifecycle.get("state", "unknown")
        duration_snapshots = lifecycle.get("duration_snapshots", 1)
        
        # Decay older narratives slightly (they've had time to mature)
        # But boost if they're in growth/momentum phase
        temporal_factor = 1.0
        if state == "emerging":
            temporal_factor = 1.1  # Boost emerging narratives
        elif state == "fade":
            temporal_factor = 0.7  # Reduce fading narratives
        elif state == "momentum":
            temporal_factor = 1.2  # Strong boost for momentum
        elif duration_snapshots > 8:
            temporal_factor = max(0.9, 1.0 - (duration_snapshots - 8) * 0.02)  # Decay old narratives
        
        # Compute final pressure with enhanced factors
        acceleration_factor = abs(velocity) if velocity else 1
        raw = velocity * acceleration_factor * impact * temporal_factor
        final = raw * stability
        
        # Determine direction from velocity
        if velocity > 0:
            direction = "up"
        elif velocity < 0:
            direction = "down"
        else:
            direction = "neutral"
        
        output.append({
            "cluster_id": cluster_id,
            "final_pressure": round(float(final), 3),
            "direction": direction,
            "state": state,
            "temporal_factor": round(temporal_factor, 3)
        })
    
    out_file = vel_path.name.replace("velocity", "final_pressure")
    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("Final pressure computed (with temporal decay & lifecycle awareness)")
