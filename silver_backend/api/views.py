from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
import os
import subprocess
import sys
import threading

PROJECT_ROOT = Path(__file__).resolve().parents[2]
snap = PROJECT_ROOT / "data" / "snapshots"
REPORT_PATH = snap / "final_report.json"
REFRESH_LOCK = threading.Lock()


def report_is_stale():
    if not REPORT_PATH.exists():
        return True
    max_age_minutes = int(os.environ.get("SILVER_ALPHA_REFRESH_MINUTES", "30"))
    mtime = datetime.fromtimestamp(REPORT_PATH.stat().st_mtime, timezone.utc)
    return datetime.now(timezone.utc) - mtime > timedelta(minutes=max_age_minutes)


def maybe_refresh_report():
    if os.environ.get("SILVER_ALPHA_AUTO_REFRESH", "true").lower() != "true":
        return
    if not report_is_stale():
        return
    if not REFRESH_LOCK.acquire(blocking=False):
        return
    try:
        if not report_is_stale():
            return
        python_bin = PROJECT_ROOT / "venv" / "bin" / "python"
        executable = str(python_bin) if python_bin.exists() else sys.executable
        subprocess.run(
            [executable, "run_pipeline.py"],
            cwd=PROJECT_ROOT,
            timeout=int(os.environ.get("SILVER_ALPHA_REFRESH_TIMEOUT", "900")),
            check=False,
        )
    finally:
        REFRESH_LOCK.release()


def load_report():
    maybe_refresh_report()
    with open(REPORT_PATH, encoding="utf-8") as f:
        return json.load(f)


def safe_get(items, index, default=None):
    if index < len(items):
        return items[index]
    return default


def get_pressure(cluster, fallback=0):
    return cluster.get('final_pressure', cluster.get('pressure', fallback))


def cluster_for_narrative(report, narrative, index):
    clusters = report.get('market', {}).get('clusters', [])
    cluster_id = narrative.get("cluster_id")
    for cluster in clusters:
        if cluster.get("cluster_id") == cluster_id:
            return cluster
    return safe_get(clusters, index, {})

@api_view(['GET'])
def globe_nodes(request):
    try:
        report = load_report()

        nodes = []
        for i, narrative in enumerate(report.get('narratives', [])):
            narrative_locations = narrative.get("locations", [])
            if not narrative_locations:
                continue

            loc = narrative_locations[0]
            cluster = cluster_for_narrative(report, narrative, i)
            pressure = get_pressure(cluster, narrative.get('pressure', 0))
            direction = "up" if pressure > 0 else "down" if pressure < 0 else "neutral"
            nodes.append({
                "id": i,
                "region": loc.get("region", loc.get("name")),
                "location": loc.get("name"),
                "lat": loc["lat"],
                "lon": loc["lon"],
                "direction": direction,
                "sentiment": 1 if direction == "up" else -1 if direction == "down" else 0,
                "narrative": narrative['narrative'],
                "pressure": pressure,
                "size": narrative['size'],
                "stability": narrative['stability'],
                "locationEvidence": loc.get("evidence", []),
                "locationMentions": loc.get("mentions", 0),
            })
        
        return Response({"status": "success", "data": nodes})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def node_detail(request, node_id):
    try:
        report = load_report()
        
        if node_id >= len(report['narratives']):
            return Response({"status": "error", "message": "Node not found"}, status=404)
        
        narrative = report['narratives'][node_id]
        cluster = cluster_for_narrative(report, narrative, node_id)
        pressure = get_pressure(cluster, narrative.get('pressure', 0))
        
        time_series = narrative.get("time_series", [])
        if not time_series:
            time_series = [{"time": 0, "value": narrative.get("size", 0)}]
        
        action_state = "WATCH"
        if abs(pressure) > 0.2:
            action_state = "BUY" if pressure > 0 else "SELL"
        
        detail = {
            "id": node_id,
            "narrative": narrative['narrative'],
            "narrative_score": round((narrative['size'] / 20) * 10, 1),
            "trust_level": "High" if narrative['stability'] > 0.8 else "Medium" if narrative['stability'] > 0.6 else "Low",
            "action_state": action_state,
            "sentiment": "bullish" if pressure > 0 else "bearish" if pressure < 0 else "neutral",
            "time_series": time_series,
            "indicators": {
                "size": round((narrative['size'] / 20) * 100, 1),
                "velocity": round(abs(pressure) * 100, 1),
                "stability": round(narrative['stability'] * 100, 1),
                "sources": narrative.get("source_count", len(narrative.get("sources", [])))
            },
            "metrics": {
                "pressure": pressure,
                "direction": cluster.get('direction', narrative.get('direction', 'neutral')),
                "cluster_size": narrative['size']
            },
            "horizon": "Short" if abs(pressure) > 0.15 else "Medium",
            "sourcesList": narrative.get("sources", []),
            "locations": narrative.get("locations", []),
        }
        
        return Response({"status": "success", "data": detail})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def dashboard_summary(request):
    try:
        report = load_report()
        
        bullish = sum(1 for c in report['market']['clusters'] if get_pressure(c) > 0)
        bearish = sum(1 for c in report['market']['clusters'] if get_pressure(c) < 0)
        neutral = len(report['market']['clusters']) - bullish - bearish
        
        summary = {
            "market_pressure_index": report['market']['market_pressure_index'],
            "regime": report['regime']['regime'],
            "trust": report['signal_trust']['signal_trust'],
            "sentiment_distribution": {
                "bullish": bullish,
                "bearish": bearish,
                "neutral": neutral
            },
            "horizons": report['multi_horizon'],
            "total_narratives": len(report['narratives']),
            "timestamp": report['timestamp']
        }
        
        return Response({"status": "success", "data": summary})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def chart_data(request):
    try:
        report = load_report()
        
        bullish = sum(1 for c in report['market']['clusters'] if get_pressure(c) > 0)
        bearish = sum(1 for c in report['market']['clusters'] if get_pressure(c) < 0)
        neutral = len(report['market']['clusters']) - bullish - bearish
        
        chart = {
            "labels": ["Bullish", "Bearish", "Neutral"],
            "values": [bullish, bearish, neutral],
            "colors": ["#00ff41", "#ff0048", "#888888"]
        }
        
        return Response({"status": "success", "data": chart})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def status(request):
    return Response({
        "status": "success",
        "message": "Silver Alpha API Online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_stale": report_is_stale(),
    })
