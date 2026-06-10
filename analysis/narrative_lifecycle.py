import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

snap_dir = Path("data/snapshots")


def load_latest_velocity():
    """Load the most recent velocity data."""
    files = sorted(snap_dir.glob("velocity_*.json"))
    if not files:
        return None
    return json.load(open(files[-1]))


def load_velocity_history(limit=20):
    """Load recent velocity history for trend analysis."""
    files = sorted(snap_dir.glob("velocity_*.json"))
    if len(files) < 2:
        return []
    
    # Load last N snapshots
    history = []
    for vf in files[-limit:]:
        try:
            data = json.load(open(vf))
            timestamp = extract_timestamp(vf.name)
            history.append({"timestamp": timestamp, "velocity_data": data})
        except Exception:
            continue
    
    return history


def extract_timestamp(filename):
    """Extract timestamp from velocity_YYYY-MM-DD_HH-MM.json"""
    try:
        parts = filename.replace("velocity_", "").replace(".json", "")
        return parts
    except Exception:
        return None


def load_lifecycle_state():
    """Load stored lifecycle state if it exists."""
    state_file = snap_dir / "narrative_lifecycle_state.json"
    if state_file.exists():
        return json.load(open(state_file))
    return {}


def save_lifecycle_state(state):
    """Persist lifecycle state for next run."""
    state_file = snap_dir / "narrative_lifecycle_state.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def classify_narrative_state(cluster_id, velocity_now, velocity_history, prev_state):
    """
    Classify narrative state based on velocity trajectory.
    
    States:
    - emerging: brand new, no history
    - growth: velocity increasing or high and recent
    - momentum: sustained strong velocity (3+ snapshots)
    - saturation: velocity declining from peak
    - fade: velocity near zero and size shrinking
    """
    
    if not velocity_history:
        return "emerging"
    
    # Get historical velocities for this cluster
    cluster_velocities = []
    for hist in velocity_history:
        for v in hist.get("velocity_data", []):
            if v.get("cluster_id") == cluster_id:
                cluster_velocities.append({
                    "velocity": v.get("velocity", 0),
                    "size": v.get("size", 0),
                    "timestamp": hist.get("timestamp")
                })
    
    if not cluster_velocities:
        return "emerging"  # Not seen before in history
    
    # Analyze trajectory
    recent_velocities = cluster_velocities[-5:] if len(cluster_velocities) >= 5 else cluster_velocities
    velocities = [v["velocity"] for v in recent_velocities]
    sizes = [v["size"] for v in recent_velocities]
    
    avg_recent_velocity = sum(velocities) / len(velocities) if velocities else 0
    velocity_now = velocities[-1] if velocities else 0
    size_now = sizes[-1] if sizes else 0
    
    # State machine logic
    if len(recent_velocities) == 1 or (len(cluster_velocities) <= 2 and velocity_now > 0):
        return "emerging"  # Very new or just appeared
    
    if len(velocities) >= 3:
        # Check for sustained momentum
        strong_count = sum(1 for v in velocities if v > 0.5)
        if strong_count >= len(velocities) * 0.6:  # 60%+ strong periods
            return "momentum"
    
    # Check for growth phase
    if velocity_now > avg_recent_velocity * 0.7 and velocity_now > 0:
        # Velocity is strong relative to average
        if len(velocities) >= 2 and velocities[-1] > velocities[-2]:
            return "growth"
    
    # Check for saturation (peak passing)
    if len(velocities) >= 3:
        max_vel = max(velocities[:-1]) if len(velocities) > 1 else velocities[0]
        if velocity_now < max_vel * 0.5 and velocity_now > 0 and size_now > 3:
            return "saturation"
    
    # Check for fade
    if velocity_now <= 0 or (size_now < 3 and avg_recent_velocity < 0.5):
        return "fade"
    
    # Default to growth if positive
    return "growth" if velocity_now > 0 else "saturation"


def build_narrative_lifecycle(velocity_data, velocity_history, prev_lifecycle_state):
    """
    Build lifecycle tracking for all narratives.
    
    Returns:
    {
        "cluster_id": {
            "state": "emerging|growth|momentum|saturation|fade",
            "entered_at": "timestamp",
            "duration_snapshots": 3,
            "velocity_trend": [1, 3, 5, 4, 2],
            "peak_size": 12,
            "current_size": 8
        }
    }
    """
    lifecycle = {}
    prev_state_dict = {s["cluster_id"]: s for s in prev_lifecycle_state} if isinstance(prev_lifecycle_state, list) else {}
    
    for v in velocity_data:
        cluster_id = v.get("cluster_id")
        velocity_now = v.get("velocity", 0)
        size_now = v.get("size", 0)
        
        # Determine state
        state = classify_narrative_state(cluster_id, velocity_now, velocity_history, prev_state_dict)
        
        # Get previous entry
        prev_entry = prev_state_dict.get(cluster_id, {})
        prev_state_val = prev_entry.get("state")
        entered_at = prev_entry.get("entered_at")
        duration = prev_entry.get("duration_snapshots", 0)
        peak_size = prev_entry.get("peak_size", size_now)
        velocity_trend = prev_entry.get("velocity_trend", [])[-4:]  # Keep last 4
        
        # Update tracking
        if state != prev_state_val:
            # State changed - reset entry time and duration
            entered_at = datetime.now(timezone.utc).isoformat()
            duration = 1
        else:
            # Same state - increment duration
            duration += 1
        
        # Update peak size
        peak_size = max(peak_size, size_now)
        
        # Update velocity trend
        velocity_trend.append(velocity_now)
        if len(velocity_trend) > 5:
            velocity_trend = velocity_trend[-5:]
        
        lifecycle[cluster_id] = {
            "cluster_id": cluster_id,
            "state": state,
            "entered_at": entered_at,
            "duration_snapshots": min(duration, 100),  # Cap at 100
            "velocity_trend": [round(v, 2) for v in velocity_trend],
            "peak_size": peak_size,
            "current_size": size_now,
            "current_velocity": round(velocity_now, 3)
        }
    
    return lifecycle


if __name__ == "__main__":
    # Load data
    velocity_data = load_latest_velocity()
    if not velocity_data:
        print("No velocity data found")
        exit()
    
    velocity_history = load_velocity_history(limit=20)
    prev_lifecycle = load_lifecycle_state()
    
    # Compute lifecycle states
    lifecycle = build_narrative_lifecycle(velocity_data, velocity_history, prev_lifecycle.values() if prev_lifecycle else [])
    
    # Save outputs
    out_file = snap_dir / "narrative_lifecycle.json"
    with open(out_file, "w") as f:
        json.dump(list(lifecycle.values()), f, indent=2)
    
    # Persist state for next run
    save_lifecycle_state(lifecycle)
    
    # Summary
    states_count = {}
    for entry in lifecycle.values():
        state = entry["state"]
        states_count[state] = states_count.get(state, 0) + 1
    
    print("Narrative lifecycle computed:")
    for state, count in sorted(states_count.items()):
        print(f"  {state}: {count} narratives")
