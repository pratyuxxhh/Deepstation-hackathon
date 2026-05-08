here will the info about backend and env datas and all

routing should be handled be the repo creator
Here is the dedicated **Backend PRD** for Project ClearGrid. This document is stripped of UI concerns and focuses entirely on data models, API endpoints, routing logic, and agent orchestration.
*"Act as a senior backend engineer. Read this PRD and initialize the FastAPI project with the defined data models and mock data generation."*

---

# ⚙️ BACKEND PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Framework:** FastAPI (Python 3.10+)
**Status:** Hackathon MVP

## 1. Backend Architecture Overview

The backend acts as the "Hive Mind" for the ClearGrid swarm. For the hackathon MVP, we do not have physical IoT sensors. Therefore, the backend will:

1. Procedurally generate and maintain the "Mock State" of 20 dustbins.
2. Execute the **Dispatcher Agent** logic (TSP Routing) on demand.
3. Execute the **Protocol Agent** logic (RAG / LLM Integration) on demand.
4. Serve this data to the Next.js frontend via RESTful API endpoints.

## 2. Technology Stack

* **Web Framework:** `fastapi`, `uvicorn`
* **Data Validation:** `pydantic`
* **Routing Algorithm (TSP):** `networkx` or Google `ortools` (use whichever the AI finds faster to implement for 20 nodes).
* **LLM Orchestration:** `langchain` (or direct API calls to OpenAI/Gemini) for the RAG agent.
* **Database:** In-memory Python dictionary (re-initialized with randomized states on server restart for fast MVP testing).

---

## 3. Core Data Models (Pydantic Schemas)

The backend must define these strict typing schemas.

### 3.1 The `BinNode` Model

```python
from pydantic import BaseModel
from typing import Optional

class Location(BaseModel):
    lat: float
    lng: float

class BinNode(BaseModel):
    node_id: str
    location: Location
    current_fill_percentage: int  # 0 to 100
    time_to_next_cycle_hrs: float
    predicted_overflow_hrs: float
    hazard_detected: bool
    hazard_classification: Optional[str] = None # e.g., "Lithium Battery", "Medical Syringe"
    collection_required: bool
    collection_reason: Optional[str] = None # "FULL", "PREDICTIVE_OVERFLOW", "HAZARD"

```

### 3.2 The `RouteResponse` Model

```python
from typing import List

class RouteResponse(BaseModel):
    optimized_path: List[BinNode]
    total_distance_km: float
    skipped_bins_count: int

```

---

## 4. API Endpoints

### 4.1 `GET /api/v1/bins`

* **Purpose:** Returns the current state of the entire grid.
* **Logic:** Returns the in-memory array of `BinNode` objects.
* **Response:** `List[BinNode]`

### 4.2 `GET /api/v1/route`

* **Purpose:** Triggers the **Dispatcher Agent** to calculate the optimal path.
* **Logic Requirements:**
1. Filter the global bin list. Keep a bin ONLY IF `current_fill_percentage >= 80` OR `predicted_overflow_hrs < time_to_next_cycle_hrs` OR `hazard_detected == True`.
2. Define a fixed "Depot" starting coordinate (e.g., a central point in Bengaluru).
3. Run a Traveling Salesperson Problem (TSP) heuristic to sort the filtered bins by shortest path distance.


* **Response:** `RouteResponse`

### 4.3 `POST /api/v1/protocol`

* **Purpose:** Triggers the **HazMat Protocol Officer (RAG)**.
* **Payload:** `{ "hazard_classification": "Lithium Battery" }`
* **Logic Requirements:**
1. Take the hazard string.
2. Inject it into an LLM prompt: *"You are an Indian Municipal Safety AI. A garbage driver just encountered {hazard_classification}. Give a strict 2-sentence safety instruction compliant with the OSH Code 2020 and Solid Waste Management Rules 2016."*
3. Return the generated text.


* **Response:** `{ "safety_instruction": "String response from LLM..." }`

---

## 5. Agent Implementation & Mocking Strategy

Since we are mocking the hardware (Sensors/Cameras), here is how the Agents are implemented in the Python backend:

* **Agent 1 (Vision) & Agent 2 (Forecaster) -> Handled by a Generator Script**
* Create a `utils/mock_generator.py` file. On server startup, it generates 20 `BinNode` objects with realistic Lat/Lng coordinates.
* Use random number generation to assign `current_fill_percentage`.
* Math Logic: Set `time_to_next_cycle_hrs` to `24.0` for all bins. Use a randomizer to set `predicted_overflow_hrs` between `2.0` and `48.0`.
* Ensure exactly 2 bins randomly get `hazard_detected = True` with a classification.
* Backend eval: If `fill > 80` or `predicted < next_cycle`, set `collection_required = True`.


* **Agent 3 (Dispatcher) -> Handled by `/api/v1/route**`
* Use the Haversine formula to calculate distances between coordinates for the TSP solver.


* **Agent 4 (Protocol RAG) -> Handled by `/api/v1/protocol**`
* Keep it lightweight. Do not build a massive vector database for a 24-hour hackathon unless you have extra time. Use a "Few-Shot Prompt" approach with the LLM API, feeding it the legal context directly in the system prompt to simulate RAG.



---

## 6. Execution Steps for Agentic IDE (Cursor / Windsurf)

**IDE INSTRUCTIONS: Please execute these steps sequentially.**

1. **Setup:** Initialize a Python virtual environment. Install `fastapi`, `uvicorn`, `pydantic`, `networkx` (or `ortools`), `python-dotenv`, and the `openai` or `google-generativeai` SDK. Create `main.py`.
2. **Schema Definition:** Create `models.py` and implement the Pydantic schemas exactly as defined in Section 3.
3. **State Management:** Create `mock_data.py`. Write a function to generate a list of 20 `BinNode` objects clustered in a 5km radius in Bengaluru (e.g., near Indiranagar). Save this to a global variable so the state persists while the server is running.
4. **Base Endpoints:** Implement `GET /api/v1/bins`. Test it via Swagger UI (localhost:8000/docs).
5. **Routing Logic:** Implement the TSP logic in `services/optimizer.py`. Create the `GET /api/v1/route` endpoint. Ensure the filtering logic (only routing to full/proactive/hazardous bins) works correctly.
6. **LLM Integration:** Create `services/rag_agent.py`. Set up the LLM API call with the Indian legal context prompt. Implement `POST /api/v1/protocol`. Add CORS middleware to `main.py` so the Next.js frontend can connect.