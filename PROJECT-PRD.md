whole project info 
# 📄 MASTER PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Platform:** Web Application (Command Center Dashboard)
**Status:** Hackathon MVP

## 1. Product Vision & Overview

Project ClearGrid is an advanced, multi-agent waste orchestration platform that transforms static municipal garbage collection into a dynamic, proactive digital grid. It operates as a "cyber-physical swarm," deploying specialized AI agents to eliminate route inefficiencies, prevent bin overflows, and handle hazardous waste autonomously.

Instead of reactive collection (picking up empty bins or cleaning up overflows), ClearGrid uses predictive forecasting, computer vision, and retrieval-augmented generation (RAG) to route drivers *only* to bins that need attention, while providing real-time safety protocols for dangerous materials.

## 2. Core Problems Addressed

1. **Inefficient Routing:** Garbage trucks waste fuel and time visiting bins that are only 10% full.
2. **Public Health Hazards:** Bins overflow unexpectedly due to local events or surges before the scheduled truck arrives.
3. **Hazardous Contamination:** Citizens throw dangerous items (lithium batteries, medical waste) into standard bins, putting drivers and landfills at risk.

## 3. The Swarm Architecture (Multi-Agent System)

The system is powered by four distinct, interacting AI agents:

* **Agent 1: The Vision Edge Node (Detection)**
* **Role:** Analyzes the contents of the bin.
* **Function:** Calculates current `fill_level` (%) and actively classifies waste types to detect anomalies or hazardous items (e.g., "Exposed Lithium Battery").


* **Agent 2: The Forecaster (Predictive ML)**
* **Role:** Predicts future state.
* **Function:** Analyzes historical fill rates, local demographics, and current fill levels to calculate `time_to_overflow`. It alerts the system if a bin will overflow *before* the next cycle, even if it is currently not full.


* **Agent 3: The Dispatcher (TSP Optimizer)**
* **Role:** The routing brain.
* **Function:** Ignores empty bins. It takes the coordinates of bins that are full (or predicted to overflow soon) and solves the Traveling Salesperson Problem (TSP) to generate the most fuel-efficient, dynamic GPS route for the driver.


* **Agent 4: The HazMat Protocol Officer (RAG)**
* **Role:** Exception handling and safety.
* **Function:** When Agent 1 detects a hazard, this agent queries a vector database of guidelines and municipal disposal guidelines. It dynamically generates localized, context-aware safety instructions for the driver and triggers Agent 3 to reroute the truck to a specialized facility if necessary.



## 4. Target User Flow (The Hackathon Demo)

The MVP will be demonstrated through the perspective of a municipal garbage truck driver logging into their daily dashboard.

1. **Dashboard Initialization:** The driver logs into the ClearGrid Web UI.
2. **The Grid View:** The main interface displays a live map of the assigned ward. Dustbins (nodes) are color-coded:
* *Green:* Empty / Ignore
* *Yellow:* Filling up / Predicted to overflow soon
* *Red:* Full / Collection Required
* *Purple Warning:* Hazardous Material Detected


3. **Route Generation:** The Dispatcher Agent activates, ignoring the green nodes and drawing an optimized polyline (route) connecting the starting location to the required bins.
4. **The RAG Trigger :** The driver selects a pulsing orange node on the route. The UI opens a HazMat Alert HUD. The Protocol Agent displays a dynamically generated safety brief (e.g., *"Warning: Lithium Battery. Do not compress. Use Class-D gloves."*) and updates the final drop-off location.

## 5. Technology Stack Overview

* **Application Framework:** React / Next.js (for building a highly responsive, modern dashboard).
* **AI & Orchestration:** Python (FastAPI) for backend logic, routing algorithms, and multi-agent orchestration (LangChain/LangGraph).
* **Mapping:** Leaflet.js or Mapbox API for plotting coordinates and routes.
* **Data Layer:** JSON structures representing simulated IoT sensor and camera data for the hackathon MVP.
* **LLM Engine:** Gemini or OpenAI API to power the RAG Protocol Agent's safety instructions.

## 6. Core Data Entities

The system relies on a central node structure representing the state of each dustbin:

```json
{
  "node_id": "BIN_402",
  "location": { "lat": 12.9716, "lng": 77.5946 },
  "current_fill_percentage": 82,
  "predicted_overflow_hrs": 1.2,
  "hazard_detected": true,
  "hazard_classification": "Lithium-Ion Battery",
  "collection_required": true
}

```

## 7. Success Criteria for MVP

* The map successfully renders and updates based on the node data.
* The routing algorithm actively skips nodes that do not require collection.
* The RAG agent successfully generates coherent, accurate safety instructions based on the injected hazard type.