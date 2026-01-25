from datetime import datetime, timedelta
import os
import time

end_date = datetime(2026, 1, 24)
start_date = datetime(2025, 7, 24)

current = start_date
run_count = 0

print("=" * 60)
print("STARTING 6-MONTH BACKFILL (Every 4th Day)")
print("=" * 60)
print(f"Start: {start_date.strftime('%d/%m/%Y')}")
print(f"End: {end_date.strftime('%d/%m/%Y')}")
print(f"Expected snapshots: ~45")
print(f"Estimated time: 90-120 minutes")
print("=" * 60)
print()

while current <= end_date:
    date_str = current.strftime('%Y-%m-%d')
    day_name = current.strftime('%A')
    
    print(f"[{run_count + 1}/45] {date_str} ({day_name})...", end=" ", flush=True)
    
    exit_code = os.system(f"python run_pipeline.py {date_str} > /dev/null 2>&1")
    
    if exit_code == 0:
        print("✓")
    else:
        print("✗")
    
    run_count += 1
    current += timedelta(days=4)
    time.sleep(1)

print()
print("=" * 60)
print(f"BACKFILL COMPLETE!")
print(f"Processed: {run_count} days")
print("=" * 60)
print("\nRun: python show_evolution.py")