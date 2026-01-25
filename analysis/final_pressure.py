import json
from pathlib import Path

snap_dir = Path("data/snapshots")

def latest(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} found")
        exit()
    return files[-1]

if __name__ == "__main__":
    vel_path = latest("velocity_*.json")
    with open(vel_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    
    output = []
    for c in clusters:
        velocity = c.get("velocity", 0)
        acceleration = c.get("acceleration", 0)  # Will be 0 on first run
        impact = c.get("impact_score", 1)
        stability = c.get("stability", 1)
        
        raw = velocity * max(abs(acceleration), 0.1) * impact
        final = raw * stability
        
        # Determine direction from velocity
        if velocity > 0:
            direction = "up"
        elif velocity < 0:
            direction = "down"
        else:
            direction = "neutral"
        
        output.append({
            "cluster_id": c["cluster_id"],
            "final_pressure": round(float(final), 3),
            "direction": direction
        })
    
    out_file = vel_path.name.replace("velocity", "final_pressure")
    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("Final pressure computed")