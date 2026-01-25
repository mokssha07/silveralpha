import json
import random
from pathlib import Path
from datetime import datetime, timedelta

snap = Path("data/snapshots")
snap.mkdir(exist_ok=True)

base_date = datetime(2026, 1, 24)

narratives = [
    "Federal Reserve Rate Policy",
    "Industrial Silver Demand",
    "Dollar Strength Impact",
    "Mining Supply Constraints",
    "Investment Flows"
]

for days_ago in range(30, -1, -3):
    date = base_date - timedelta(days=days_ago)
    date_str = date.strftime("%Y-%m-%d_%H-%M")
    
    clusters = []
    for i, narrative in enumerate(narratives):
        clusters.append({
            "cluster_id": i,
            "narrative": narrative,
            "size": random.randint(8, 18),
            "stability": round(random.uniform(0.6, 0.95), 2),
            "pressure": round(random.uniform(-0.3, 0.3), 2),
            "direction": random.choice(["up", "down", "neutral"])
        })
    
    with open(snap / f"clusters_{date_str}.json", "w") as f:
        json.dump(clusters, f, indent=2)

velocities = []
for i in range(len(narratives)):
    velocities.append({
        "cluster_id": i,
        "velocity": round(random.uniform(-2, 2), 1)
    })

with open(snap / "velocity_latest.json", "w") as f:
    json.dump(velocities, f, indent=2)

pressures = []
for i in range(len(narratives)):
    pressures.append({
        "cluster_id": i,
        "final_pressure": round(random.uniform(-0.3, 0.3), 2),
        "direction": random.choice(["up", "down", "neutral"])
    })

with open(snap / "final_pressure_latest.json", "w") as f:
    json.dump(pressures, f, indent=2)

mpi = round(sum(p["final_pressure"] for p in pressures) / len(pressures), 3)

market_index = {
    "market_pressure_index": mpi,
    "clusters": pressures
}

with open(snap / "market_index_latest.json", "w") as f:
    json.dump(market_index, f, indent=2)

regime = "momentum" if abs(mpi) > 0.15 else "building" if abs(mpi) > 0.05 else "quiet"

final_report = {
    "market": market_index,
    "confidence": {"confidence": 0.72, "source": "historical_validation"},
    "regime": {"regime": regime},
    "signal_trust": {"signal_trust": 0.85 if regime == "momentum" else 0.65},
    "multi_horizon": {
        "short_term": round(random.uniform(-0.15, 0.15), 2),
        "medium_term": round(random.uniform(-0.10, 0.10), 2),
        "long_term": round(random.uniform(-0.05, 0.05), 2)
    },
    "narratives": clusters,
    "timestamp": datetime.now().isoformat()
}

with open(snap / "final_report.json", "w") as f:
    json.dump(final_report, f, indent=2)

print(f"✓ Generated {len(list(snap.glob('clusters_*.json')))} cluster snapshots")
print(f"✓ Market Pressure Index: {mpi}")
print(f"✓ Regime: {regime}")
print(f"✓ Final report created")
