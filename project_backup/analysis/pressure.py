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
    impact_path = latest("impact_*.json")

    with open(impact_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    output = []

    for c in clusters:
        velocity = c["size"]
        acceleration = 1  # first snapshot fallback

        raw_pressure = velocity * acceleration * c["impact_score"]

        final_pressure = (
            raw_pressure *
            c["stability"]
        )

        output.append({
            "cluster_id": c["cluster_id"],
            "pressure": round(float(final_pressure), 3),
            "direction": c["direction"]
        })

    out_file = impact_path.name.replace("impact", "pressure")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Pressure scoring complete")
