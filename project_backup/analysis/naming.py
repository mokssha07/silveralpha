import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

snap_dir = Path("data/snapshots")

path = sorted(snap_dir.glob("clusters_*.json"))[-1]

with open(path, "r", encoding="utf-8") as f:
    clusters = json.load(f)

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=4
)

for c in clusters:
    texts = [d["text"] for d in c["documents"]]
    tfidf = vectorizer.fit_transform(texts)
    keywords = vectorizer.get_feature_names_out()
    c["name"] = " / ".join(keywords)

out_file = path.name.replace("clusters", "named_clusters")

with open(snap_dir / out_file, "w", encoding="utf-8") as f:
    json.dump(clusters, f, indent=2, ensure_ascii=False)

print("Narratives named")
