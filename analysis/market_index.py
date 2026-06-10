import json
from pathlib import Path

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
    pressure_path = latest("final_pressure_*.json")
    with open(pressure_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)
    
    total = sum(abs(c["final_pressure"]) for c in clusters)
    signed = sum(c["final_pressure"] for c in clusters)
    
    market_index = 0
    if total > 0:
        market_index = signed / total
    
    clusters_out = []
    for c in clusters:
        clusters_out.append({
            "cluster_id": c["cluster_id"],
            "final_pressure": c["final_pressure"],
            "pressure": c["final_pressure"],
            "direction": c["direction"]
        })
    
    output = {
        "market_pressure_index": round(float(market_index), 3),
        "clusters": clusters_out
    }
    
    out_file = pressure_path.name.replace("final_pressure", "market_index")
    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("Market index computed")
