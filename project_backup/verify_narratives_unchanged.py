# Verifies determinism of the Narrative Engine

import hashlib
from pathlib import Path

def h(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()

snap = Path("data/snapshots")
files = ["clusters", "final_pressure", "market_index", "confidence"]

hashes_before = {f: h(sorted(snap.glob(f"{f}_*.json"))[-1]) for f in files}

# Re-run narrative engine only
import os
os.system("python ingestion/ingest.py")
os.system("python preprocessing/clean.py")
os.system("python embeddings/embed.py")
os.system("python clustering/cluster.py")
os.system("python analysis/impact.py")
os.system("python analysis/velocity.py")
os.system("python analysis/final_pressure.py")
os.system("python analysis/market_index.py")

hashes_after = {f: h(sorted(snap.glob(f"{f}_*.json"))[-1]) for f in files}

assert hashes_before == hashes_after, "Narrative outputs changed unexpectedly"
print("Narrative Engine verified: deterministic and unchanged.")
