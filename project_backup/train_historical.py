import subprocess

with open("training_dates.txt") as f:
    dates = [d.strip() for d in f if d.strip()]

for d in dates:
    print(f"\n=== Training date {d} ===")
    subprocess.run(["python", "run_pipeline.py", d], check=True)