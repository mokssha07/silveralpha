import subprocess
from datetime import datetime, timedelta

START_DATE = datetime(2025, 7, 24)
END_DATE = datetime(2026, 1, 24)

RUN_DAYS = [0, 2, 4]  # 3 times a week
cur = START_DATE

dates = []

while cur <= END_DATE:
    if cur.weekday() in RUN_DAYS:
        dates.append(cur.strftime("%Y-%m-%d"))
    cur += timedelta(days=1)

print(f"Training on {len(dates)} dates")

for d in dates:
    print("\n=== Training date", d, "===")
    subprocess.run(["python", "run_pipeline.py", d], check=True)

print("\nHistorical training complete")