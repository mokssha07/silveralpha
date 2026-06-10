import json
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

snap = Path("data/snapshots")
files = sorted(snap.glob("clusters_*.json"))
impact_files = sorted(snap.glob("impact_*.json"))
impact_by_cluster = {}

if impact_files:
    impact_rows = json.load(open(impact_files[-1]))
    impact_by_cluster = {
        row.get("cluster_id"): row
        for row in impact_rows
    }

if len(files) < 2:
    print("Not enough snapshots")
    if len(files) == 1:
        curr = json.load(open(files[-1]))
        velocity = []
        for c in curr:
            impact_row = impact_by_cluster.get(c["cluster_id"], {})
            velocity.append({
                "cluster_id": c["cluster_id"],
                "velocity": 0,
                "size": c.get("size", 0),
                "stability": c.get("stability", 1),
                "impact_score": impact_row.get("impact_score", c.get("impact_score", 1))
            })
        out = snap / files[-1].name.replace("clusters_", "velocity_")
        json.dump(velocity, open(out, "w"), indent=2)
        print("Bootstrap velocity created (all zeros)")
    exit()

prev = json.load(open(files[-2]))
curr = json.load(open(files[-1]))


def get_cluster_centroid(cluster):
    """Extract centroid from cluster for semantic matching."""
    centroid = cluster.get("centroid")
    if centroid is not None:
        return np.array(centroid)
    return None


def best_previous_match_semantic(current, previous, current_centroid, prev_centroids):
    """Match narratives using semantic similarity on cluster centroids."""
    if current_centroid is None:
        return None

    best = None
    best_score = 0.0
    
    for idx, candidate in enumerate(previous):
        prev_centroid = prev_centroids.get(idx)
        if prev_centroid is None:
            continue
        
        try:
            score = cosine_similarity(
                [current_centroid],
                [prev_centroid]
            )[0][0]
        except Exception:
            continue
        
        if score > best_score and score > 0.35:
            best = (idx, candidate)
            best_score = score

    return best if best_score > 0.35 else None


def best_previous_match_fallback(current, previous):
    """Fallback: text-based matching for backwards compatibility."""
    from difflib import SequenceMatcher
    
    def cluster_text(cluster):
        docs = cluster.get("documents", [])
        if docs:
            return " ".join(doc.get("text", "") for doc in docs[:5]).lower()
        return cluster.get("narrative", "").lower()
    
    current_text = cluster_text(current)
    if not current_text:
        return None

    best = None
    best_score = 0.0
    for idx, candidate in enumerate(previous):
        candidate_text = cluster_text(candidate)
        if not candidate_text:
            continue
        score = SequenceMatcher(None, current_text[:500], candidate_text[:500]).ratio()
        if score > best_score:
            best = (idx, candidate)
            best_score = score


    return best if best_score >= 0.45 else None

# Build centroid map for semantic matching
prev_centroids = {}
for idx, cluster in enumerate(prev):
    centroid = get_cluster_centroid(cluster)
    if centroid is not None:
        prev_centroids[idx] = centroid

velocity = []
for c_now in curr:
    current_centroid = get_cluster_centroid(c_now)
    
    # Try semantic matching first (primary method)
    if current_centroid is not None and prev_centroids:
        match_result = best_previous_match_semantic(c_now, prev, current_centroid, prev_centroids)
        if match_result:
            _, match = match_result
            v = c_now["size"] - match["size"]
        else:
            v = 0
    else:
        # Fallback to text-based matching for backwards compatibility
        match_result = best_previous_match_fallback(c_now, prev)
        if match_result:
            _, match = match_result
            v = c_now["size"] - match["size"]
        else:
            v = 0
    
    impact_row = impact_by_cluster.get(c_now["cluster_id"], {})

    velocity.append({
        "cluster_id": c_now["cluster_id"],
        "velocity": v,
        "size": c_now.get("size", 0),
        "stability": c_now.get("stability", 1),
        "impact_score": impact_row.get("impact_score", c_now.get("impact_score", 1))
    })

out = snap / files[-1].name.replace("clusters_", "velocity_")
json.dump(velocity, open(out, "w"), indent=2)
print("Velocity computed (semantic matching enabled)")
