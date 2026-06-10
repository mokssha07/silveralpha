import json
import numpy as np
from pathlib import Path
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from analysis.geo import merge_locations

snap_dir = Path("data/snapshots")


def latest_file(pattern):
    files = sorted(snap_dir.glob(pattern))
    if not files:
        print(f"No {pattern} files found")
        raise SystemExit(1)
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

    if len(docs) < 3:
        output = []
        if docs:
            output.append({
                "cluster_id": 0,
                "size": len(docs),
                "stability": 1.0,
                "source_count": len({doc.get("source") for doc in docs if doc.get("source")}),
                "sources": sorted({doc.get("source") for doc in docs if doc.get("source")}),
                "locations": merge_locations(docs),
                "documents": docs
            })
        out_file = txt_path.name.replace("clean_snapshot", "clusters")
        with open(snap_dir / out_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Found {len(output)} small-sample clusters")
        exit()

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

    if not clusters and docs:
        clusters[0] = docs
        labels = np.zeros(len(docs), dtype=int)

    output = []

    for label, items in clusters.items():
        idx = labels == label
        sims = cosine_similarity(embeddings[idx])
        mean_similarity = float(sims.mean())
        stability = max(0.0, min(1.0, mean_similarity))

        sources = sorted({item.get("source") for item in items if item.get("source")})

        # Compute cluster centroid for semantic matching in velocity calculation
        centroid = embeddings[idx].mean(axis=0).tolist()

        output.append({
            "cluster_id": int(label),
            "size": int(len(items)),
            "stability": float(round(stability, 3)),
            "source_count": len(sources),
            "sources": sources,
            "locations": merge_locations(items),
            "centroid": centroid,
            "documents": items
        })

    out_file = txt_path.name.replace("clean_snapshot", "clusters")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Found {len(output)} clusters")
