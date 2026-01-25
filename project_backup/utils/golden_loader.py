from pathlib import Path
import shutil

snap_dir = Path("data/snapshots")
gold_dir = Path("data/golden")


def ensure_file(live_pattern, golden_name):
    files = sorted(snap_dir.glob(live_pattern))
    if files:
        return files[-1]

    print(f"Using golden fallback for {golden_name}")
    target = snap_dir / golden_name
    shutil.copy(gold_dir / golden_name, target)
    return target
