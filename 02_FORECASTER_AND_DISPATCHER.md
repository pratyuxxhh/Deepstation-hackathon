# PRD 02 — Agent 2 (Forecaster) + Agent 3 (Dispatcher / TSP Router)
**File:** `backend/agents/forecaster.py` + `backend/agents/dispatcher.py` + `backend/routers/route.py`

---

## Objective

Implement the predictive overflow forecaster and the TSP-based route optimizer. Together these two agents form the core routing intelligence: the Forecaster flags bins that will overflow before the next collection cycle, and the Dispatcher builds an optimized multi-stop route visiting only necessary bins.

---

## Agent 2: The Forecaster

**File:** `backend/agents/forecaster.py`

### Logic

The Forecaster runs a simple heuristic on each bin:

```
if predicted_overflow_hrs < time_to_next_cycle_hrs:
    bin.collection_required = True
    bin.collection_reason = "PREDICTIVE_OVERFLOW"
    bin.status_color = "BLUE"  (unless already PURPLE or RED)
```

The mock data already has these fields pre-populated. The Forecaster validates and re-computes them at runtime to demonstrate the agent is active.

### Implementation

```python
# backend/agents/forecaster.py

def run_forecaster(bins: list[dict]) -> list[dict]:
    """
    Agent 2: Predictive overflow analysis.
    Re-evaluates each bin's BLUE flag based on overflow vs cycle timing.
    Mutates status_color only if current color is GREEN.
    Returns the updated bin list.
    """
    for bin in bins:
        # Never override PURPLE (hazard takes precedence)
        if bin["hazard_detected"]:
            continue
        
        will_overflow_before_collection = (
            bin["predicted_overflow_hrs"] < bin["time_to_next_cycle_hrs"]
        )
        
        if will_overflow_before_collection and bin["status_color"] == "GREEN":
            bin["status_color"] = "BLUE"
            bin["collection_required"] = True
            bin["collection_reason"] = "PREDICTIVE_OVERFLOW"
    
    return bins
```

---

## Agent 3: The Dispatcher (TSP Optimizer)

**File:** `backend/agents/dispatcher.py`

### Dual-Filter Logic

The Dispatcher ignores GREEN bins entirely. It builds a route from bins that meet **either** of these conditions:
1. `status_color == "RED"` — currently full (>=80%)
2. `status_color == "BLUE"` — forecasted to overflow before next cycle
3. `status_color == "PURPLE"` — hazard detected (always included, rerouted to disposal)

### TSP Algorithm

Use the **Nearest Neighbor Heuristic** for hackathon speed:
1. Start from the depot (driver's current location / garage)
2. At each step, visit the nearest unvisited required bin
3. Return distance is not needed — open route (no return to depot)

Distance calculation: **Haversine formula** between lat/lng coordinates.

### Implementation

```python
# backend/agents/dispatcher.py

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
    h = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
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
```

---

## Route Router

**File:** `backend/routers/route.py`

```python
from fastapi import APIRouter
from data.loader import load_bins
from agents.forecaster import run_forecaster
from agents.dispatcher import build_route

router = APIRouter(tags=["Route"])

@router.get("/route")
def get_optimized_route():
    """
    Runs the full agent pipeline:
    Agent 1 (precomputed in mock data) → Agent 2 (Forecaster) → Agent 3 (Dispatcher)
    Returns TSP-optimized route for all required bins.
    """
    bins = load_bins()
    bins = run_forecaster(bins)
    route = build_route(bins)
    return route
```

---

## Response Schema

```json
{
  "depot": { "lat": 12.9352, "lng": 77.5947 },
  "waypoints": [
    {
      "node_id": "BIN_219",
      "location": { "lat": 12.9634, "lng": 77.5877 },
      "status_color": "PURPLE",
      "hazard_classification": "Exposed Lithium Battery",
      ...
    }
  ],
  "total_distance_km": 14.7,
  "polyline": [[12.9352, 77.5947], [12.9634, 77.5877], ...],
  "skipped_count": 8,
  "summary": { "red": 4, "blue": 4, "purple": 4 }
}
```

---

## Acceptance Criteria

- [ ] `GET /api/v1/route` returns a valid route object
- [ ] `waypoints` contains only RED, BLUE, and PURPLE bins (no GREEN)
- [ ] `polyline` starts at depot coordinates
- [ ] `total_distance_km` is a positive float
- [ ] `summary` correctly counts bins by color
- [ ] `skipped_count` equals the number of GREEN bins
- [ ] Route order follows nearest-neighbor logic (visually verifiable on map)
- [ ] PURPLE bins appear in waypoints (not skipped)
