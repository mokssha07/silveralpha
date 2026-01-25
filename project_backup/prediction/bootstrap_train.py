import json
import random
from pathlib import Path

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"
snap.mkdir(parents=True, exist_ok=True)

rows = []

for _ in range(60):
    market_pressure_index = random.uniform(0.3, 1.8)
    num_narratives = random.randint(1, 7)
    max_cluster_pressure = random.uniform(0.2, 1.6)
    mean_confidence = random.uniform(0.4, 0.9)

    score = (
        0.4 * market_pressure_index +
        0.3 * max_cluster_pressure +
        0.3 * mean_confidence
    )

    label = 1 if score > 0.9 else 0

    rows.append({
        "market_pressure_index": round(market_pressure_index, 3),
        "num_narratives": num_narratives,
        "max_cluster_pressure": round(max_cluster_pressure, 3),
        "mean_confidence": round(mean_confidence, 3),
        "label": label
    })

json.dump(rows, open(mem_path, "w"), indent=2)
print("Bootstrapped training memory with 60 realistic samples")
