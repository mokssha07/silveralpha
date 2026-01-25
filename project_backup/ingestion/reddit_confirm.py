import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

snap = Path("data/snapshots")
reddit_dir = Path("data/reddit")

clusters_file = sorted(snap.glob("clusters_*.json"))[-1]
embeddings_file = sorted(snap.glob("embeddings_*.npy"))[-1]

clusters = json.load(open(clusters_file))
cluster_embeddings = np.load(embeddings_file)

model = SentenceTransformer("all-MiniLM-L6-v2")

def load_reddit_posts():
    posts = []
    for f in reddit_dir.glob("reddit_*.json"):
        posts.extend(json.load(open(f)))
    return posts

reddit_posts = load_reddit_posts()
if not reddit_posts:
    print("No reddit posts found")
    exit()

texts = [(p["title"] + " " + p["text"]).strip() for p in reddit_posts]
reddit_vecs = model.encode(texts)

assignments = {}

for vec, post in zip(reddit_vecs, reddit_posts):
    sims = cosine_similarity([vec], cluster_embeddings)[0]
    best = sims.argmax()
    if sims[best] < 0.65:
        continue
    cid = clusters[best]["cluster_id"]
    assignments.setdefault(cid, []).append(post)

out = snap / "reddit_confirmation.json"
json.dump(assignments, open(out, "w"), indent=2)
print(f"Reddit confirmations added to {len(assignments)} clusters")
