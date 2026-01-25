import json
from pathlib import Path

snap_dir = Path("data/snapshots")


if __name__ == "__main__":
    cluster_path = sorted(snap_dir.glob("clusters_*.json"))[-1]
    pressure_path = sorted(snap_dir.glob("weighted_pressure_*.json"))[-1]

    with open(cluster_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    with open(pressure_path, "r", encoding="utf-8") as f:
        pressures = json.load(f)

    cluster_info = {}

    for c in clusters:
        sources = {d["source"] for d in c["documents"]}
        cluster_info[c["cluster_id"]] = {
            "stability": c["stability"],
            "diversity": len(sources),
            "size": c["size"]
        }

    output = []

    for p in pressures:
        info = cluster_info.get(p["cluster_id"])
        if not info:
            continue

        confidence = (
            info["stability"] *
            (1 + 0.15 * info["diversity"]) *
            (1 + info["size"] / 10)
        )

        output.append({
            "cluster_id": p["cluster_id"],
            "weighted_pressure": p["weighted_pressure"],
            "confidence": round(float(confidence), 3),
            "direction": p["direction"]
        })

    out_file = pressure_path.name.replace("weighted_pressure", "confidence")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print("Narrative confidence computed")
