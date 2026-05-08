from fastapi import APIRouter

router = APIRouter(tags=["Route"])

@router.get("/route")
def get_route():
    """Returns TSP-optimized route. Placeholder — agent logic in Phase 2."""
    return {"waypoints": [], "total_distance_km": 0, "polyline": [], "depot": {"lat": 12.9716, "lng": 77.5946}}
