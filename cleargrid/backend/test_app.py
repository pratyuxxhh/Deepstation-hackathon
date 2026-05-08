"""Quick smoke test for ClearGrid API scaffold."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Test 1: Health endpoint
r = client.get("/health")
print(f"GET /health => {r.status_code} {r.json()}")
assert r.status_code == 200
assert r.json() == {"status": "ok", "service": "ClearGrid API"}

# Test 2: Bins endpoint
r = client.get("/api/v1/bins")
print(f"GET /api/v1/bins => {r.status_code} (count: {len(r.json())})")
assert r.status_code == 200
bins = r.json()
assert len(bins) == 20

# Verify distribution
from collections import Counter
colors = Counter(b["status_color"] for b in bins)
print(f"Distribution: {dict(colors)}")
assert colors["GREEN"] == 8
assert colors["RED"] == 4
assert colors["BLUE"] == 4
assert colors["PURPLE"] == 4

# Test 3: Route stub
r = client.get("/api/v1/route")
print(f"GET /api/v1/route => {r.status_code} {r.json()}")
assert r.status_code == 200

# Test 4: HazMat stub
r = client.get("/api/v1/hazmat/BIN_401")
print(f"GET /api/v1/hazmat/BIN_401 => {r.status_code} {r.json()}")
assert r.status_code == 200

print("\n✅ All tests passed!")
