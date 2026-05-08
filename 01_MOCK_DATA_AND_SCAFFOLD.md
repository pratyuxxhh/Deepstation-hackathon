# PRD 01 — Mock Data & Backend Scaffold
**Agent:** None (foundational setup)
**File:** `backend/data/mock_bins.json` + `backend/main.py`

---

## Objective

Bootstrap the FastAPI backend with realistic mock IoT bin data for Bengaluru Ward 68. All four agents read from this data source. The backend must be runnable with a single command.

---

## Task 1: Create Mock Bin Data

**File:** `backend/data/mock_bins.json`

Create a JSON array of 20 bin nodes. Distribution must include:
- 8 GREEN bins (fill < 80%, no overflow risk, no hazard)
- 4 RED bins (fill >= 80%, no hazard)
- 4 BLUE bins (fill < 80% but `predicted_overflow_hrs < time_to_next_cycle_hrs`)
- 3 PURPLE bins (hazard detected — vary hazard types)
- 1 PURPLE + RED bin (fill >= 80% AND hazard detected — PURPLE always wins)

**Hazard types to use:**
- `"Exposed Lithium Battery"`
- `"Medical Waste (Syringes)"`
- `"Unlabeled Chemical Drum"`

**Coordinate range:** Bengaluru area — lat between 12.91 and 12.98, lng between 77.55 and 77.65

**Example entries:**

```json
[
  {
    "node_id": "BIN_101",
    "location": { "lat": 12.9352, "lng": 77.6245 },
    "current_fill_percentage": 12,
    "time_to_next_cycle_hrs": 24.0,
    "predicted_overflow_hrs": 96.0,
    "hazard_detected": false,
    "hazard_classification": null,
    "collection_required": false,
    "collection_reason": null,
    "status_color": "GREEN"
  },
  {
    "node_id": "BIN_402",
    "location": { "lat": 12.9716, "lng": 77.5946 },
    "current_fill_percentage": 45,
    "time_to_next_cycle_hrs": 24.0,
    "predicted_overflow_hrs": 14.5,
    "hazard_detected": false,
    "hazard_classification": null,
    "collection_required": true,
    "collection_reason": "PREDICTIVE_OVERFLOW",
    "status_color": "BLUE"
  },
  {
    "node_id": "BIN_317",
    "location": { "lat": 12.9521, "lng": 77.6089 },
    "current_fill_percentage": 88,
    "time_to_next_cycle_hrs": 18.0,
    "predicted_overflow_hrs": 3.0,
    "hazard_detected": false,
    "hazard_classification": null,
    "collection_required": true,
    "collection_reason": "FULL",
    "status_color": "RED"
  },
  {
    "node_id": "BIN_219",
    "location": { "lat": 12.9634, "lng": 77.5877 },
    "current_fill_percentage": 55,
    "time_to_next_cycle_hrs": 20.0,
    "predicted_overflow_hrs": 8.0,
    "hazard_detected": true,
    "hazard_classification": "Exposed Lithium Battery",
    "collection_required": true,
    "collection_reason": "HAZMAT",
    "status_color": "PURPLE"
  }
]
```

Generate all 20 bins following the distribution above. Vary fill percentages, cycle times, and coordinates realistically.

---

## Task 2: FastAPI Application Shell

**File:** `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import bins, route, hazmat

app = FastAPI(title="ClearGrid API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bins.router, prefix="/api/v1")
app.include_router(route.router, prefix="/api/v1")
app.include_router(hazmat.router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "ok", "service": "ClearGrid API"}
```

---

## Task 3: Requirements File

**File:** `backend/requirements.txt`

```
fastapi==0.111.0
uvicorn[standard]==0.30.1
anthropic==0.28.0
python-dotenv==1.0.1
pydantic==2.7.4
```

---

## Task 4: Data Loader Utility

**File:** `backend/data/loader.py`

```python
import json
from pathlib import Path
from functools import lru_cache

DATA_PATH = Path(__file__).parent / "mock_bins.json"

@lru_cache(maxsize=1)
def load_bins() -> list[dict]:
    with open(DATA_PATH) as f:
        return json.load(f)
```

---

## Task 5: Bins Router (Passthrough)

**File:** `backend/routers/bins.py`

```python
from fastapi import APIRouter
from data.loader import load_bins

router = APIRouter(tags=["Bins"])

@router.get("/bins")
def get_bins():
    """Returns all bin nodes with precomputed status_color."""
    return load_bins()
```

---

## Acceptance Criteria

- [ ] `uvicorn main:app --reload` starts without errors
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `GET /api/v1/bins` returns array of 20 bin objects
- [ ] Each bin has all required fields: `node_id`, `location`, `current_fill_percentage`, `time_to_next_cycle_hrs`, `predicted_overflow_hrs`, `hazard_detected`, `hazard_classification`, `collection_required`, `collection_reason`, `status_color`
- [ ] Distribution: 8 GREEN, 4 RED, 4 BLUE, 4 PURPLE (3 + 1 combo)
- [ ] PURPLE bins have `hazard_detected: true` regardless of fill level
