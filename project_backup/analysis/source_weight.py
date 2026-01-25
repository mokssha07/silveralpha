import json
from pathlib import Path

snap_dir = Path("data/snapshots")

source_weights = {
    "Mining.com": 1.2,
    "Kitco": 1.1,
    "Reddit": 0.8,
    "Unknown": 0.6
}


def get_weight(source):
    return source_weights.get(source, source_weights["Unknown"])


if __name__ == "__main__":
    cluster_path = sorted(snap_dir.glob("clusters_*.json"))[-1]
    pressure_path = sorted(snap_dir.glob("adjusted_pressure_*.json"))[-1]

    with open(cluster_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    with open(pressure_path, "r", encoding="utf-8") as f:
        pressures = json.load(f)

    cluster_weight = {}

    for c in clusters:
        weights = [get_weight(d["source"]) for d in c["documents"]]
        cluster_weight[c["cluster_id"]] = sum(weights) / len(weights)

    output = []

    for p in pressures:
        w = cluster_weight.get(p["cluster_id"], 1.0)
        output.append({
            "cluster_id": p["cluster_id"],
            "weighted_pressure": round(p["adjusted_pressure"] * w, 3),
            "direction": p["direction"]
        })

    out_file = pressure_path.name.replace("adjusted_pressure", "weighted_pressure")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Source-weighted pressure computed")
