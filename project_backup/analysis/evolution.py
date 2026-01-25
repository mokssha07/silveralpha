import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

snap_dir = Path("data/snapshots")

cluster_files = sorted(snap_dir.glob("clusters_*.json"))
embed_files = sorted(snap_dir.glob("embeddings_*.npy"))

if len(cluster_files) < 2 or len(embed_files) < 2:
    print("Not enough snapshots for evolution analysis")
    exit()

prev_c, curr_c = cluster_files[-2], cluster_files[-1]
prev_e, curr_e = embed_files[-2], embed_files[-1]

with open(prev_c, "r", encoding="utf-8") as f:
    prev_clusters = json.load(f)

with open(curr_c, "r", encoding="utf-8") as f:
    curr_clusters = json.load(f)

E_prev = np.load(prev_e)
E_curr = np.load(curr_e)

prev_centroid = E_prev.mean(axis=0, keepdims=True)
curr_centroid = E_curr.mean(axis=0, keepdims=True)

sim = cosine_similarity(curr_centroid, prev_centroid)[0][0]

if sim > 0.9:
    status = "merged"
elif sim < 0.7:
    status = "diverged"
else:
    status = "stable"

output = {
    "previous_snapshot": prev_c.name,
    "current_snapshot": curr_c.name,
    "similarity": round(float(sim), 3),
    "evolution": status
}

out_file = curr_c.name.replace("clusters", "evolution")

with open(snap_dir / out_file, "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("Narrative evolution detected:", status)
