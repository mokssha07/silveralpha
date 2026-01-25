import json
from pathlib import Path

snap = Path("data/snapshots")
files = sorted(snap.glob("final_report.json"))

if files:
    report = json.load(open(files[-1]))
    
    print("\n=== MARKET STATE ===")
    print(f"Pressure Index: {report['market']['market_pressure_index']}")
    print(f"Regime: {report['regime']['regime']}")
    print(f"Trust: {report['signal_trust']['signal_trust']}")
    
    print("\n=== MULTI-HORIZON ===")
    mh = report['multi_horizon']
    print(f"Short-term:  {mh['short_term']:+.2f}")
    print(f"Medium-term: {mh['medium_term']:+.2f}")
    print(f"Long-term:   {mh['long_term']:+.2f}")
    
    print("\n=== CLUSTER PRESSURES ===")
    for c in report['market']['clusters']:
        print(f"Cluster {c['cluster_id']}: {c['final_pressure']:+.2f} ({c['direction']})")
    
    print("\n=== NARRATIVES ===")
    for n in report['narratives'][:5]:
        print(f"{n['narrative']}: Size={n['size']}, Stability={n['stability']}")