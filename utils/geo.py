import math
from typing import Optional

CITY_COORDS: dict[str, tuple[float, float]] = {
    "South Bend, IN": (41.6764, -86.2520),
    "Fort Wayne, IN": (41.0793, -85.1394),
    "Indianapolis, IN": (39.7684, -86.1581),
    "Bloomington, IN": (39.1653, -86.5264),
    "West Lafayette, IN": (40.4259, -86.9081),
    "Detroit, MI": (42.3314, -83.0458),
    "Grand Rapids, MI": (42.9634, -85.6681),
    "Ann Arbor, MI": (42.2808, -83.7430),
    "Evanston, IL": (42.0451, -87.6877),
    "Springfield, IL": (39.7817, -89.6501),
    "Chicago, IL": (41.8781, -87.6298),
    "Champaign, IL": (40.1164, -88.2434),
    "Columbus, OH": (39.9612, -82.9988),
    "Dayton, OH": (39.7589, -84.1916),
    "Cleveland, OH": (41.4993, -81.6944),
    "Cincinnati, OH": (39.1031, -84.5120),
    "Milwaukee, WI": (43.0389, -87.9065),
    "Madison, WI": (43.0731, -89.4012),
    "Muncie, IN": (40.1934, -85.3864),
    "Terre Haute, IN": (39.4667, -87.4139),
    "New York, NY": (40.7128, -74.0060),
}

# State abbreviation to full name mapping
STATE_NAMES: dict[str, str] = {
    "IN": "Indiana",
    "IL": "Illinois",
    "OH": "Ohio",
    "MI": "Michigan",
    "WI": "Wisconsin",
    "CA": "California",
    "NY": "New York",
}

# Adjacent states for family proximity scoring
ADJACENT_STATES: dict[str, set[str]] = {
    "IN": {"IL", "OH", "MI", "KY"},
    "IL": {"IN", "WI", "IA", "MO", "KY"},
    "OH": {"IN", "MI", "PA", "WV", "KY"},
    "MI": {"IN", "OH", "WI"},
    "WI": {"IL", "MI", "MN", "IA"},
}


def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def get_distance(city1: str, city2: str) -> Optional[float]:
    coords1 = CITY_COORDS.get(city1)
    coords2 = CITY_COORDS.get(city2)
    if coords1 and coords2:
        return round(haversine_miles(*coords1, *coords2), 1)
    return None


def extract_state(location: str) -> str:
    if ", " in location:
        return location.split(", ")[-1].strip()
    return ""


def get_state_full_name(abbrev: str) -> str:
    return STATE_NAMES.get(abbrev, abbrev)


def are_adjacent(state1: str, state2: str) -> bool:
    return state2 in ADJACENT_STATES.get(state1, set())
