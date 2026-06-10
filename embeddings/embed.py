import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer


snap_dir = Path("data/snapshots")
out_dir = Path("data/snapshots")
out_dir.mkdir(parents=True, exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")


def load_latest_snapshot():
    files = sorted(snap_dir.glob("clean_snapshot_*.json"))
    if not files:
        print("No cleaned snapshots found")
        raise SystemExit(1)
    return files[-1]


if __name__ == "__main__":
    path = load_latest_snapshot()

    with open(path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    texts = [d["text"] for d in docs]
    if not texts:
        print("No cleaned documents to embed")
        raise SystemExit(1)

    embeddings = model.encode(texts, show_progress_bar=True)

    out_file = path.name.replace("clean_snapshot", "embeddings").replace(".json", ".npy")
    np.save(out_dir / out_file, embeddings)

    print(f"Saved embeddings: {embeddings.shape}")
