import json
from pathlib import Path
from ftfy import fix_text
from cleantext import clean
from analysis.geo import extract_locations

raw_dir = Path("data/raw")
out_dir = Path("data/snapshots")

out_dir.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    text = fix_text(text)
    text = clean(
        text,
        fix_unicode=False,
        to_ascii=False,
        lower=True,
        no_urls=True,
        no_emails=True,
        no_numbers=False,
        no_punct=False
    )
    return text.strip()


def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = []

    for d in data:
        if "text" in d and not d.get("title"):
            text = d.get("text", "")
        else:
            text = f"{d.get('title', '')} {d.get('summary', d.get('description', ''))}"
        text = clean_text(text)

        if len(text) < 50:
            continue

        cleaned.append({
            "source": d.get("source"),
            "text": text,
            "published": d.get("published", d.get("date")),
            "url": d.get("url", d.get("link")),
            "locations": extract_locations(text),
        })

    return cleaned


if __name__ == "__main__":
    files = sorted(raw_dir.glob("*_snapshot_*.json"))

    if not files:
        print("No raw snapshots found")
        raise SystemExit(1)

    latest = max(files, key=lambda path: path.stat().st_mtime)
    cleaned_docs = process_file(latest)

    if "snapshot_" in latest.name:
        suffix = latest.name.split("snapshot_", 1)[1]
        out_file = out_dir / f"clean_snapshot_{suffix}"
    else:
        out_file = out_dir / f"clean_snapshot_{latest.stem}.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_docs, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(cleaned_docs)} cleaned documents")
