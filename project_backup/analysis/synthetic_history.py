import json
import random
from pathlib import Path
from copy import deepcopy
from datetime import datetime, timedelta

snap = Path("data/snapshots")

base_file = sorted(snap.glob("clusters_*.json"))[-1]
base = json.load(open(base_file))

base_time = datetime.utcnow()

for i in range(1, 6):
    fake = deepcopy(base)

    for c in fake:
        c["size"] = max(1, int(c["size"] * random.uniform(0.7, 1.2)))
        c["stability"] = round(c["stability"] * random.uniform(0.85, 1.1), 3)

    t = base_time - timedelta(hours=4 * i)
    name = f"clusters_{t.strftime('%Y-%m-%d_%H-%M')}.json"

    json.dump(fake, open(snap / name, "w"), indent=2)

print("Synthetic historical clusters created")
