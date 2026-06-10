import re
from collections import Counter


LOCATIONS = [
    {"name": "Washington, DC", "region": "United States", "lat": 38.9072, "lon": -77.0369, "aliases": ["federal reserve", "fomc", "washington"]},
    {"name": "New York", "region": "United States", "lat": 40.7128, "lon": -74.0060, "aliases": ["new york", "wall street", "comex", "nyse", "cme"]},
    {"name": "Chicago", "region": "United States", "lat": 41.8781, "lon": -87.6298, "aliases": ["chicago"]},
    {"name": "London", "region": "United Kingdom", "lat": 51.5074, "lon": -0.1278, "aliases": ["london", "lbma", "bank of england", "financial times"]},
    {"name": "Brussels", "region": "European Union", "lat": 50.8503, "lon": 4.3517, "aliases": ["european union", "eu ", "brussels", "eurozone", "ecb"]},
    {"name": "Frankfurt", "region": "Germany", "lat": 50.1109, "lon": 8.6821, "aliases": ["frankfurt", "european central bank"]},
    {"name": "Beijing", "region": "China", "lat": 39.9042, "lon": 116.4074, "aliases": ["china", "chinese", "beijing", "pboc"]},
    {"name": "Shanghai", "region": "China", "lat": 31.2304, "lon": 121.4737, "aliases": ["shanghai", "shanghai futures exchange"]},
    {"name": "Tokyo", "region": "Japan", "lat": 35.6762, "lon": 139.6503, "aliases": ["japan", "tokyo", "boj"]},
    {"name": "Mumbai", "region": "India", "lat": 19.0760, "lon": 72.8777, "aliases": ["india", "indian", "mumbai"]},
    {"name": "New Delhi", "region": "India", "lat": 28.6139, "lon": 77.2090, "aliases": ["new delhi", "delhi"]},
    {"name": "Mexico City", "region": "Mexico", "lat": 19.4326, "lon": -99.1332, "aliases": ["mexico", "mexican", "mexico city"]},
    {"name": "Lima", "region": "Peru", "lat": -12.0464, "lon": -77.0428, "aliases": ["peru", "peruvian", "lima"]},
    {"name": "Santiago", "region": "Chile", "lat": -33.4489, "lon": -70.6693, "aliases": ["chile", "chilean", "santiago"]},
    {"name": "Buenos Aires", "region": "Argentina", "lat": -34.6037, "lon": -58.3816, "aliases": ["argentina", "buenos aires"]},
    {"name": "Toronto", "region": "Canada", "lat": 43.6532, "lon": -79.3832, "aliases": ["canada", "canadian", "toronto"]},
    {"name": "Ottawa", "region": "Canada", "lat": 45.4215, "lon": -75.6972, "aliases": ["ottawa"]},
    {"name": "Saskatchewan", "region": "Canada", "lat": 52.9399, "lon": -106.4509, "aliases": ["saskatchewan"]},
    {"name": "Sydney", "region": "Australia", "lat": -33.8688, "lon": 151.2093, "aliases": ["australia", "australian", "sydney"]},
    {"name": "Perth", "region": "Australia", "lat": -31.9523, "lon": 115.8613, "aliases": ["perth", "western australia"]},
    {"name": "Johannesburg", "region": "South Africa", "lat": -26.2041, "lon": 28.0473, "aliases": ["south africa", "johannesburg"]},
    {"name": "Moscow", "region": "Russia", "lat": 55.7558, "lon": 37.6173, "aliases": ["russia", "russian", "moscow"]},
    {"name": "Kyiv", "region": "Ukraine", "lat": 50.4501, "lon": 30.5234, "aliases": ["ukraine", "ukrainian", "kyiv", "kiev"]},
    {"name": "Riyadh", "region": "Saudi Arabia", "lat": 24.7136, "lon": 46.6753, "aliases": ["saudi arabia", "riyadh", "opec"]},
    {"name": "Dubai", "region": "United Arab Emirates", "lat": 25.2048, "lon": 55.2708, "aliases": ["dubai", "uae", "united arab emirates"]},
    {"name": "Singapore", "region": "Singapore", "lat": 1.3521, "lon": 103.8198, "aliases": ["singapore"]},
    {"name": "Hong Kong", "region": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "aliases": ["hong kong"]},
]


def _alias_pattern(alias):
    alias = alias.strip().lower()
    if alias.endswith(" "):
        return re.compile(rf"\b{re.escape(alias.strip())}\b", re.IGNORECASE)
    return re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)


ALIAS_INDEX = [
    (location, alias, _alias_pattern(alias))
    for location in LOCATIONS
    for alias in location["aliases"]
]


def extract_locations(text):
    if not text:
        return []

    hits = Counter()
    evidence = {}
    for location, alias, pattern in ALIAS_INDEX:
        matches = pattern.findall(text)
        if not matches:
            continue
        key = location["name"]
        hits[key] += len(matches)
        evidence.setdefault(key, set()).add(alias.strip())

    results = []
    by_name = {location["name"]: location for location in LOCATIONS}
    for name, count in hits.most_common():
        location = by_name[name]
        results.append({
            "name": location["name"],
            "region": location["region"],
            "lat": location["lat"],
            "lon": location["lon"],
            "mentions": count,
            "evidence": sorted(evidence[name]),
        })
    return results


def merge_locations(documents):
    merged = {}
    for doc in documents:
        for location in doc.get("locations", []):
            name = location["name"]
            current = merged.setdefault(name, {
                "name": location["name"],
                "region": location["region"],
                "lat": location["lat"],
                "lon": location["lon"],
                "mentions": 0,
                "evidence": set(),
            })
            current["mentions"] += location.get("mentions", 1)
            current["evidence"].update(location.get("evidence", []))

    locations = []
    for location in merged.values():
        location["evidence"] = sorted(location["evidence"])
        locations.append(location)

    return sorted(locations, key=lambda item: item["mentions"], reverse=True)
