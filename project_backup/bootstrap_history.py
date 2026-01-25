import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

snap_dir = Path("data/snapshots")

cluster_files = sorted(snap_dir.glob("clusters_*.json"))
embedding_files = sorted(snap_dir.glob("embeddings_*.npy"))

if not cluster_files or not embedding_files:
    print("No base snapshots found. Run pipeline once first.")
    exit()

today_clusters = json.load(open(cluster_files[-1]))
today_embeddings = np.load(embedding_files[-1])

base_time = datetime.now()

for days_ago in range(7, 0, -1):
    target_time = base_time - timedelta(days=days_ago)
    date_str = target_time.strftime("%Y-%m-%d_%H-%M")
    
    noise = np.random.normal(0, 0.05 * days_ago, today_embeddings.shape)
    fake_embeddings = today_embeddings + noise
    
    fake_clusters = []
    for c in today_clusters:
        fake_c = c.copy()
        fake_c["size"] = max(1, c["size"] + np.random.randint(-3, 4))
        fake_clusters.append(fake_c)
    
    np.save(snap_dir / f"embeddings_{date_str}.npy", fake_embeddings)
    with open(snap_dir / f"clusters_{date_str}.json", "w") as f:
        json.dump(fake_clusters, f, indent=2)
    
    print(f"Created snapshot for {date_str}")

print("History created")