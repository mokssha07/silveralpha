from datetime import datetime, timedelta
import os
import time

start_date = datetime(2024, 1, 10)
end_date = datetime(2024, 1, 24)

current = start_date

print("Starting historical backfill...")
print(f"Date range: {start_date.date()} to {end_date.date()}")
print()

run_count = 0

while current <= end_date:
    date_str = current.strftime('%Y-%m-%d')
    print(f"[{run_count + 1}] Processing {date_str}...")
    
    exit_code = os.system(f"python run_pipeline.py {date_str}")
    
    if exit_code != 0:
        print(f"ERROR: Pipeline failed on {date_str}")
        break
    
    run_count += 1
    current += timedelta(days=1)
    time.sleep(2)

print()
print(f"Backfill complete! Processed {run_count} days")
print("Run 'python show_evolution.py' to see results")