from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
from pathlib import Path
import random
from datetime import datetime

snap = Path("../data/snapshots")

@api_view(['GET'])
def globe_nodes(request):
    try:
        report = json.load(open(snap / "final_report.json"))
        
        locations = [
            {"region": "North America", "lat": 40, "lon": -100},
            {"region": "Europe", "lat": 50, "lon": 10},
            {"region": "Asia", "lat": 35, "lon": 105},
            {"region": "South America", "lat": -15, "lon": -60},
            {"region": "Australia", "lat": -25, "lon": 135}
        ]
        
        nodes = []
        for i, loc in enumerate(locations):
            if i < len(report['narratives']):
                narrative = report['narratives'][i]
                pressure = report['market']['clusters'][i]['final_pressure']
                direction = "up" if pressure > 0 else "down"
                nodes.append({
                "id": i,
                "region": loc["region"],
                "lat": loc["lat"],
                "lon": loc["lon"],
                "direction": direction,
                "sentiment": 1 if direction == "up" else -1,

                "narrative": narrative['narrative'],
                 "pressure": pressure,
                "size": narrative['size'],
                "stability": narrative['stability']
                })
        
        return Response({"status": "success", "data": nodes})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def node_detail(request, node_id):
    try:
        report = json.load(open(snap / "final_report.json"))
        
        if node_id >= len(report['narratives']):
            return Response({"status": "error", "message": "Node not found"}, status=404)
        
        narrative = report['narratives'][node_id]
        cluster = report['market']['clusters'][node_id]
        
        time_series = []
        for i in range(20):
            time_series.append({
                "time": i,
                "value": narrative['size'] + random.uniform(-3, 3)
            })
        
        action_state = "WATCH"
        if abs(cluster['final_pressure']) > 0.2:
            action_state = "BUY" if cluster['final_pressure'] > 0 else "SELL"
        
        detail = {
            "id": node_id,
            "narrative": narrative['narrative'],
            "narrative_score": round((narrative['size'] / 20) * 10, 1),
            "trust_level": "High" if narrative['stability'] > 0.8 else "Medium" if narrative['stability'] > 0.6 else "Low",
            "action_state": action_state,
            "sentiment": "bullish" if cluster['final_pressure'] > 0 else "bearish",
            "time_series": time_series,
            "indicators": {
                "size": round((narrative['size'] / 20) * 100, 1),
                "velocity": round(abs(cluster['final_pressure']) * 100, 1),
                "stability": round(narrative['stability'] * 100, 1),
                "sources": random.randint(3, 8)
            },
            "metrics": {
                "pressure": cluster['final_pressure'],
                "direction": cluster['direction'],
                "cluster_size": narrative['size']
            },
            "horizon": "Short" if abs(cluster["final_pressure"]) > 0.15 else "Medium",
            "sourcesList": ["Reuters", "FT", "Mining.com"],
        }
        
        return Response({"status": "success", "data": detail})
    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(['GET'])
def dashboard_summary(request):
    try:
        report = json.load(open(snap / "final_report.json"))
        
        bullish = sum(1 for c in report['market']['clusters'] if c['final_pressure'] > 0)
        bearish = sum(1 for c in report['market']['clusters'] if c['final_pressure'] < 0)
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
        report = json.load(open(snap / "final_report.json"))
        
        bullish = sum(1 for c in report['market']['clusters'] if c['final_pressure'] > 0)
        bearish = sum(1 for c in report['market']['clusters'] if c['final_pressure'] < 0)
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
        "timestamp": datetime.now().isoformat()
    })
