import sys
import subprocess
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Run the Silver Alpha narrative pipeline.")
parser.add_argument("run_date", nargs="?", help="Historical date in YYYY-MM-DD format.")
parser.add_argument("--no-predictor", action="store_true", help="Skip prediction training/action update.")
parser.add_argument("--no-report", action="store_true", help="Skip final report generation.")
args = parser.parse_args()

RUN_DATE = args.run_date

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/snapshots").mkdir(parents=True, exist_ok=True)

steps = []

if RUN_DATE:
    steps.append(["-m", "ingestion.ingest_wayback", RUN_DATE])
else:
    steps.append(["-m", "ingestion.ingest"])

analysis_steps = [
    ["-m", "preprocessing.clean"],
    ["embeddings/embed.py"],
    ["-m", "clustering.cluster"],
    ["-m", "analysis.impact"],
    ["-m", "analysis.velocity"],
    ["-m", "analysis.narrative_lifecycle"],
    ["-m", "analysis.final_pressure"],
    ["-m", "analysis.market_index"],
    ["-m", "analysis.reddit_confidence"],
    ["-m", "analysis.regime_features"],
    ["-m", "analysis.regime_classify"],
    ["-m", "analysis.regime_trust"],
    ["-m", "analysis.narrative_conflict"],
    ["-m", "analysis.multi_horizon"],
]

prediction_steps = [
    ["-m", "prediction.train_predictor"],
    ["-m", "prediction.action_state"]
]

steps += analysis_steps
if not args.no_predictor:
    steps += prediction_steps

for cmd in steps:
    run_cmd = [sys.executable, *cmd]
    result = subprocess.run(run_cmd)
    if result.returncode != 0:
        print("Pipeline stopped at:", " ".join(run_cmd))
        sys.exit(1)

print("Pipeline executed successfully")

if not args.no_report:
    if RUN_DATE:
        subprocess.run([sys.executable, "build_report.py", RUN_DATE], check=True)
    else:
        subprocess.run([sys.executable, "build_report.py"], check=True)
