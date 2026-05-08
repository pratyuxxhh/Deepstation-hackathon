"""Acceptance tests for Agent 2 (Forecaster) + Agent 3 (Dispatcher) route pipeline."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=== Route Endpoint Acceptance Tests ===\n")

# --- Test: GET /api/v1/route returns 200 ---
r = client.get("/api/v1/route")
assert r.status_code == 200, f"Expected 200, got {r.status_code}"
route = r.json()
print(f"[PASS] GET /api/v1/route => {r.status_code}")

# --- Test: Response has required keys ---
required_keys = {"depot", "waypoints", "total_distance_km", "polyline", "skipped_count", "summary"}
assert required_keys.issubset(route.keys()), f"Missing keys: {required_keys - route.keys()}"
print(f"[PASS] Response contains all required keys: {sorted(required_keys)}")

# --- Test: No GREEN bins in waypoints ---
waypoint_colors = [wp["status_color"] for wp in route["waypoints"]]
assert "GREEN" not in waypoint_colors, f"GREEN bins found in waypoints: {waypoint_colors}"
print(f"[PASS] No GREEN bins in waypoints (colors: {set(waypoint_colors)})")

# --- Test: Only RED, BLUE, PURPLE in waypoints ---
allowed_colors = {"RED", "BLUE", "PURPLE"}
assert set(waypoint_colors).issubset(allowed_colors), f"Unexpected colors: {set(waypoint_colors) - allowed_colors}"
print(f"[PASS] Waypoints contain only RED, BLUE, PURPLE bins")

# --- Test: Polyline starts at depot ---
depot = route["depot"]
assert route["polyline"][0] == [depot["lat"], depot["lng"]], \
    f"Polyline does not start at depot: {route['polyline'][0]} != [{depot['lat']}, {depot['lng']}]"
print(f"[PASS] Polyline starts at depot [{depot['lat']}, {depot['lng']}]")

# --- Test: total_distance_km is positive float ---
assert isinstance(route["total_distance_km"], float), f"total_distance_km is not a float: {type(route['total_distance_km'])}"
assert route["total_distance_km"] > 0, f"total_distance_km is not positive: {route['total_distance_km']}"
print(f"[PASS] total_distance_km = {route['total_distance_km']} (positive float)")

# --- Test: Summary correctly counts bins by color ---
summary = route["summary"]
actual_red = sum(1 for wp in route["waypoints"] if wp["status_color"] == "RED")
actual_blue = sum(1 for wp in route["waypoints"] if wp["status_color"] == "BLUE")
actual_purple = sum(1 for wp in route["waypoints"] if wp["status_color"] == "PURPLE")
assert summary["red"] == actual_red, f"Summary red mismatch: {summary['red']} != {actual_red}"
assert summary["blue"] == actual_blue, f"Summary blue mismatch: {summary['blue']} != {actual_blue}"
assert summary["purple"] == actual_purple, f"Summary purple mismatch: {summary['purple']} != {actual_purple}"
print(f"[PASS] Summary counts correct: red={summary['red']}, blue={summary['blue']}, purple={summary['purple']}")

# --- Test: skipped_count equals GREEN bins ---
total_bins = 20  # known from mock data
expected_skipped = total_bins - len(route["waypoints"])
assert route["skipped_count"] == expected_skipped, \
    f"skipped_count mismatch: {route['skipped_count']} != {expected_skipped}"
print(f"[PASS] skipped_count = {route['skipped_count']} (matches {expected_skipped} GREEN bins)")

# --- Test: PURPLE bins appear in waypoints ---
purple_in_route = [wp["node_id"] for wp in route["waypoints"] if wp["status_color"] == "PURPLE"]
assert len(purple_in_route) > 0, "No PURPLE bins in waypoints - they should be included!"
print(f"[PASS] PURPLE bins in route: {purple_in_route}")

# --- Test: Polyline length matches waypoints + 1 (depot) ---
assert len(route["polyline"]) == len(route["waypoints"]) + 1, \
    f"Polyline length mismatch: {len(route['polyline'])} != {len(route['waypoints']) + 1}"
print(f"[PASS] Polyline has {len(route['polyline'])} points ({len(route['waypoints'])} waypoints + depot)")

# --- Test: Forecaster doesn't override PURPLE bins ---
purple_bins = [wp for wp in route["waypoints"] if wp["status_color"] == "PURPLE"]
for pb in purple_bins:
    assert pb["hazard_detected"] is True, f"PURPLE bin {pb['node_id']} has hazard_detected=False"
    assert pb["collection_reason"] == "HAZMAT", f"PURPLE bin {pb['node_id']} reason is not HAZMAT"
print(f"[PASS] All PURPLE bins retain hazard_detected=True and reason=HAZMAT")

print(f"\n[ALL PASSED] Route endpoint meets all acceptance criteria.")
print(f"  Waypoints: {len(route['waypoints'])} bins")
print(f"  Distance:  {route['total_distance_km']} km")
print(f"  Skipped:   {route['skipped_count']} GREEN bins")
print(f"  Summary:   {summary}")
