import json
import numpy as np
from pathlib import Path
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity

snap_dir = Path("data/snapshots")


def latest_file(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} files found")
        exit()
    return files[-1]


if __name__ == "__main__":
    emb_path = latest_file("embeddings_*.npy")
    txt_path = latest_file("clean_snapshot_*.json")

    embeddings = np.load(emb_path)

    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        out_file = txt_path.name.replace("clean_snapshot", "clusters")
        with open(snap_dir / out_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print("No data to cluster")
        exit()

    with open(txt_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,
        min_samples=2,
        metric="euclidean"
    )

    labels = clusterer.fit_predict(embeddings)

    clusters = {}

    for label, doc in zip(labels, docs):
        if label == -1:
            continue
        clusters.setdefault(int(label), []).append(doc)

    output = []

    for label, items in clusters.items():
        idx = labels == label
        sims = cosine_similarity(embeddings[idx])
        variance = 1 - sims.mean()

        output.append({
            "cluster_id": int(label),
            "size": int(len(items)),
            "stability": float(round(1 / (variance + 1e-6), 3)),
            "documents": items
        })

    out_file = txt_path.name.replace("clean_snapshot", "clusters")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Found {len(output)} clusters")