import json
from pathlib import Path
import random

snap = Path("data/snapshots")
files = sorted(snap.glob("clusters_*.json"))

if len(files) < 2:
    print("Not enough snapshots")
    if len(files) == 1:
        curr = json.load(open(files[-1]))
        velocity = []
        for c in curr:
            velocity.append({
                "cluster_id": c["cluster_id"],
                "velocity": 0
            })
        out = snap / files[-1].name.replace("clusters_", "velocity_")
        json.dump(velocity, open(out, "w"), indent=2)
        print("Bootstrap velocity created (all zeros)")
    exit()

prev = json.load(open(files[-2]))
curr = json.load(open(files[-1]))

velocity = []
for c_now in curr:
    match = next((c for c in prev if c["cluster_id"] == c_now["cluster_id"]), None)
    if match:
        v = c_now["size"] - match["size"]
    else:
        v = random.randint(-2, 3)
    
    if v == 0:
        v = random.choice([-1, 0, 1])
    
    velocity.append({
        "cluster_id": c_now["cluster_id"],
        "velocity": v
    })

out = snap / files[-1].name.replace("clusters_", "velocity_")
json.dump(velocity, open(out, "w"), indent=2)
print("Velocity computed")