import json
from pathlib import Path
import math

snap_dir = Path("data/snapshots")


def latest(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} found")
        exit()
    return files[-1]


if __name__ == "__main__":
    pressure_path = latest("final_pressure_*.json")
    cluster_path = latest("clusters_*.json")

    with open(pressure_path, "r", encoding="utf-8") as f:
        pressures = json.load(f)

    with open(cluster_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    cluster_sources = {}

    for c in clusters:
        sources = {d["source"] for d in c["documents"]}
        cluster_sources[c["cluster_id"]] = len(sources)

    output = []

    for p in pressures:
        diversity_bonus = 1 + 0.15 * cluster_sources.get(p["cluster_id"], 1)
        persistence_weight = math.log(1 + 1)  # single snapshot fallback

        adjusted = p["final_pressure"] * diversity_bonus * persistence_weight

        output.append({
            "cluster_id": p["cluster_id"],
            "adjusted_pressure": round(float(adjusted), 3),
            "direction": p["direction"]
        })

    out_file = pressure_path.name.replace("final_pressure", "adjusted_pressure")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Adjusted pressure computed")
