from datetime import datetime, timedelta

start = datetime(2025, 7, 24)
end = datetime(2026, 1, 24)

dates = []
d = start

while d <= end:
    if d.weekday() in (0, 2, 4):  # Mon, Wed, Fri
        dates.append(d.strftime("%Y-%m-%d"))
    d += timedelta(days=1)

with open("training_dates.txt", "w") as f:
    for x in dates:
        f.write(x + "\n")

print(f"Generated {len(dates)} training dates")