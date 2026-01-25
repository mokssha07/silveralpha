import time
import subprocess

while True:
    subprocess.run(["python", "ingestion/ingest.py"])
    subprocess.run(["python", "preprocessing/clean.py"])
    subprocess.run(["python", "embeddings/embed.py"])
    subprocess.run(["python", "clustering/cluster.py"])
    subprocess.run(["python", "analysis/impact.py"])
    subprocess.run(["python", "analysis/velocity.py"])
    subprocess.run(["python", "analysis/final_pressure.py"])
    subprocess.run(["python", "analysis/market_index.py"])

    time.sleep(4 * 60 * 60)
