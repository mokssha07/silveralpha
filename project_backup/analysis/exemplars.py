import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

snap_dir = Path("data/snapshots")


def latest(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} found")
        exit()
    return files[-1]


if __name__ == "__main__":
    cluster_path = latest("clusters_*.json")
    embed_path = latest("embeddings_*.npy")

    with open(cluster_path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    embeddings = np.load(embed_path)

    output = []

    idx = 0
    for c in clusters:
        size = len(c["documents"])
        cluster_embs = embeddings[idx: idx + size]
        idx += size

        centroid = cluster_embs.mean(axis=0, keepdims=True)
        sims = cosine_similarity(cluster_embs, centroid).flatten()

        top_ids = sims.argsort()[-2:][::-1]

        exemplars = [c["documents"][i] for i in top_ids]

        output.append({
            "cluster_id": c["cluster_id"],
            "name": c.get("name"),
            "exemplars": exemplars
        })

    out_file = cluster_path.name.replace("clusters", "exemplars")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Cluster exemplars extracted")
