"""Agent 3: Dispatcher — TSP route optimizer."""

import math
from typing import Optional

DEPOT = {"lat": 12.9352, "lng": 77.5947}  # Ward 68 garage


def haversine_km(a: dict, b: dict) -> float:
    """Distance in km between two {lat, lng} points."""
    R = 6371
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lng"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lng"])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def filter_required_bins(bins: list[dict]) -> list[dict]:
    """Agent 3 Filter: only RED, BLUE, PURPLE bins need collection."""
    return [b for b in bins if b["status_color"] in ("RED", "BLUE", "PURPLE")]


def nearest_neighbor_tsp(required_bins: list[dict], depot: dict) -> list[dict]:
    """
    Greedy nearest-neighbor TSP heuristic.
    Returns ordered list of bins to visit.
    """
    if not required_bins:
        return []

    unvisited = required_bins.copy()
    route = []
    current_pos = depot

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda b: haversine_km(current_pos, b["location"])
        )
        route.append(nearest)
        current_pos = nearest["location"]
        unvisited.remove(nearest)

    return route


def build_route(bins: list[dict]) -> dict:
    """
    Full Dispatcher output: filtered bins + TSP ordering + metadata.
    """
    required = filter_required_bins(bins)
    ordered = nearest_neighbor_tsp(required, DEPOT)

    # Build polyline: depot → each waypoint
    polyline = [[DEPOT["lat"], DEPOT["lng"]]]
    total_distance = 0.0
    prev_loc = DEPOT

    for bin in ordered:
        loc = bin["location"]
        total_distance += haversine_km(prev_loc, loc)
        polyline.append([loc["lat"], loc["lng"]])
        prev_loc = loc

    return {
        "depot": DEPOT,
        "waypoints": ordered,
        "total_distance_km": round(total_distance, 2),
        "polyline": polyline,
        "skipped_count": len(bins) - len(required),
        "summary": {
            "red": sum(1 for b in ordered if b["status_color"] == "RED"),
            "blue": sum(1 for b in ordered if b["status_color"] == "BLUE"),
            "purple": sum(1 for b in ordered if b["status_color"] == "PURPLE"),
        }
    }
