import os
import shutil
from pathlib import Path

REQUIRED_FILES = {
    'ingestion/ingest_wayback.py',
    'ingestion/ingest.py',
    'preprocessing/clean.py',
    'embeddings/embed.py',
    'clustering/cluster.py',
    'analysis/impact.py',
    'analysis/velocity.py',
    'analysis/final_pressure.py',
    'analysis/market_index.py',
    'analysis/reddit_confidence.py',
    'analysis/regime_features.py',
    'analysis/regime_classify.py',
    'analysis/regime_trust.py',
    'analysis/narrative_conflict.py',
    'analysis/multi_horizon.py',
    'prediction/train_predictor.py',
    'prediction/action_state.py',
    'run_pipeline.py',
    'build_report.py',
    'train_historical_backfill.py',
    'show_evolution.py',
    'bootstrap_history.py'
}

REQUIRED_DIRS = {
    'data/snapshots',
    'data/raw',
    'ingestion',
    'preprocessing',
    'embeddings',
    'clustering',
    'analysis',
    'prediction'
}

print("Creating cleaned project structure...")

backup_dir = Path("project_backup")
if backup_dir.exists():
    shutil.rmtree(backup_dir)

shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns('venv', '__pycache__', '*.pyc', '.git', 'project_backup'))

print(f"Backup created at: {backup_dir}")

all_py_files = set()
for pattern in ['*.py', '*/*.py', '*/*/*.py']:
    all_py_files.update(Path('.').glob(pattern))

unused_files = []
for py_file in all_py_files:
    rel_path = str(py_file)
    if rel_path not in REQUIRED_FILES and 'venv' not in rel_path and '__pycache__' not in rel_path:
        unused_files.append(rel_path)

print(f"\nFound {len(unused_files)} unused Python files:")
for f in sorted(unused_files):
    print(f"  - {f}")

print("\nDo you want to delete these files? (yes/no): ", end="")
