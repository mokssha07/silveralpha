import argparse
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def run(cmd, quiet=False):
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.STDOUT if quiet else None
    return subprocess.run([sys.executable, *cmd], stdout=stdout, stderr=stderr).returncode


def date_range(start, end, step_days):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=step_days)


def main():
    parser = argparse.ArgumentParser(description="Backfill narrative snapshots and train predictor labels.")
    parser.add_argument("--years", type=int, default=10)
    parser.add_argument("--start")
    parser.add_argument("--end", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--step-days", type=int, default=7, help="Historical news sampling interval.")
    parser.add_argument("--horizon", type=int, default=5, help="Forward return horizon in trading days.")
    parser.add_argument("--threshold", type=float, default=0.02, help="Meaningful move threshold.")
    parser.add_argument("--skip-news", action="store_true", help="Use existing snapshots only.")
    parser.add_argument("--skip-prices", action="store_true", help="Use existing price file.")
    parser.add_argument("--skip-existing", action="store_true", help="Do not rerun dates that already have cluster snapshots.")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    end = datetime.strptime(args.end, "%Y-%m-%d")
    start = datetime.strptime(args.start, "%Y-%m-%d") if args.start else end - timedelta(days=args.years * 365)

    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/snapshots").mkdir(parents=True, exist_ok=True)
    Path("data/prices").mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("SILVER ALPHA HISTORICAL TRAINING")
    print("=" * 72)
    print(f"Window: {start.date()} -> {end.date()} ({args.years} years requested)")
    print(f"News sampling: every {args.step_days} day(s)")
    print(f"Label: abs({args.horizon}-trading-day forward return) >= {args.threshold:.2%}")
    print("=" * 72)

    if not args.skip_prices:
        code = run([
            "data/prices/fetch_silver_prices.py",
            "--start", start.strftime("%Y-%m-%d"),
            "--end", end.strftime("%Y-%m-%d"),
            "--horizons", f"1,{args.horizon},10,20",
        ], quiet=args.quiet)
        if code != 0:
            print("Price fetch failed; cannot build labels without data/prices/silver_daily.json.")
            sys.exit(code)

    if not args.skip_news:
        dates = list(date_range(start, end, args.step_days))
        for index, current in enumerate(dates, start=1):
            date_str = current.strftime("%Y-%m-%d")
            snapshot = Path("data/snapshots") / f"clusters_{date_str}_00-00.json"
            if args.skip_existing and snapshot.exists():
                print(f"[{index}/{len(dates)}] skip existing {date_str}")
                continue
            print(f"[{index}/{len(dates)}] pipeline {date_str}")
            code = run(["run_pipeline.py", date_str, "--no-predictor", "--no-report"], quiet=args.quiet)
            if code != 0:
                print(f"Pipeline failed for {date_str}; continuing with next date.")
            time.sleep(0.25)

    code = run([
        "prediction/build_training_dataset.py",
        "--horizon", str(args.horizon),
        "--threshold", str(args.threshold),
    ], quiet=args.quiet)
    if code != 0:
        sys.exit(code)

    code = run(["prediction/train_predictor.py"], quiet=args.quiet)
    if code != 0:
        sys.exit(code)

    run(["prediction/action_state.py"], quiet=args.quiet)
    run(["build_report.py"], quiet=args.quiet)
    print("Historical training complete.")


if __name__ == "__main__":
    main()
