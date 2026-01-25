import os
import sys
from pathlib import Path

RUN_DATE = sys.argv[1] if len(sys.argv) > 1 else None

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/snapshots").mkdir(parents=True, exist_ok=True)

steps = []

if RUN_DATE:
    steps.append(f"python ingestion/ingest_wayback.py {RUN_DATE}")
else:
    steps.append("python ingestion/ingest.py")

steps += [
    "python preprocessing/clean.py",
    "python embeddings/embed.py",
    "python clustering/cluster.py",
    "python analysis/impact.py",
    "python analysis/velocity.py",
    "python analysis/final_pressure.py",
    "python analysis/market_index.py",
    "python analysis/reddit_confidence.py",
    "python analysis/regime_features.py",
    "python analysis/regime_classify.py",
    "python analysis/regime_trust.py",
    "python analysis/narrative_conflict.py",
    "python analysis/multi_horizon.py",
    "python prediction/train_predictor.py",
    "python prediction/action_state.py"
]

for cmd in steps:
    exit_code = os.system(cmd)
    if exit_code != 0:
        print("Pipeline stopped at:", cmd)
        sys.exit(1)

print("Pipeline executed successfully")

if RUN_DATE:
    os.system(f"python build_report.py {RUN_DATE}")
else:
    os.system("python build_report.py")