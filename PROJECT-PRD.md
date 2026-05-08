# 📄 MASTER PRODUCT REQUIREMENTS DOCUMENT (PRD)

**Platform:** Web Application (Command Center Dashboard)
**Target Environment:** Hackathon MVP (Web UI + Simulated API Backend)

## 1. Product Vision & Overview

This is an advanced, multi-agent waste orchestration platform that transforms static municipal garbage collection into a dynamic, proactive digital grid. It operates as a "cyber-physical swarm," deploying specialized AI agents to eliminate route inefficiencies, prevent bin overflows, and handle hazardous waste autonomously.

Instead of reactive collection (picking up empty bins or cleaning up overflows), ClearGrid uses predictive forecasting, computer vision, and retrieval-augmented generation (RAG) to route drivers *only* to bins that need attention, while providing real-time, legally compliant safety protocols for dangerous materials.

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
* **Role:** Predicts future state and cycle overlap.
* **Function:** Analyzes historical fill rates, local demographics/events, and current fill levels to calculate `time_to_overflow`. It continuously compares this metric against the `time_to_next_cycle` (e.g., when the truck is scheduled to visit this neighborhood again). If `time_to_overflow` < `time_to_next_cycle`, it autonomously flags the bin for immediate pickup, preventing future messes even if the bin is currently mostly empty.


* **Agent 3: The Dispatcher (TSP Optimizer)**
* **Role:** The routing brain.
* **Function:** Operates on a dual-heuristic filter. It ignores bins unless they meet one of two conditions: 1) They are currently full (e.g., >80%), OR 2) They are flagged by the Forecaster as overlapping with the next cycle. It takes this filtered list of nodes and solves the Traveling Salesperson Problem (TSP) to generate the most fuel-efficient, dynamic GPS route.


* **Agent 4: The HazMat Protocol Officer (RAG)**
* **Role:** Exception handling, safety, and legal compliance.
* **Function:** When Agent 1 detects a hazard, this agent queries a vector database loaded with the **Solid Waste Management Rules (2016), the OSH Code (2020), and CPCB guidelines**. It dynamically generates localized, context-aware safety instructions for the driver ensuring strict compliance with Swachh Bharat Mission 2.0 mandates, and triggers Agent 3 to reroute the truck to a specialized facility if necessary.



## 4. Target User Flow (The Hackathon Demo)

The MVP will be demonstrated through the perspective of a municipal garbage truck driver logging into their daily dashboard.

1. **Dashboard Initialization:** The driver logs into the ClearGrid Web UI.
2. **The Grid View:** The main interface displays a live map of the assigned ward. Dustbins (nodes) are color-coded:
* *Green:* Empty & Safe / Ignore
* *Red:* Currently Full / Collection Required
* *Blue:* Proactive Pickup (Currently under threshold, but flagged by the Forecaster to overflow before the next collection cycle) / Collection Required
* *Purple Warning:* Hazardous Material Detected


3. **Route Generation:** The Dispatcher Agent activates, ignoring the green nodes and drawing an optimized polyline (route) connecting the starting location to the required (Red, Blue, Purple) bins.
4. **The RAG Trigger (The "Wow" Moment):** The driver selects a pulsing purple node on the route. The UI opens a HazMat Alert HUD. The Protocol Agent displays a dynamically generated safety brief citing Indian regulations (e.g., *"Warning: Lithium Battery. Per OSH Code 2020, mandate Class-D fire gloves before handling."*) and updates the final drop-off location.

## 5. Technology Stack Overview

* **Application Framework:** React / Next.js (for building a highly responsive, modern dashboard with Tailwind CSS).
* **AI & Orchestration:** Python (FastAPI) for backend logic, routing algorithms, and multi-agent orchestration.
* **Mapping:** Leaflet.js (react-leaflet) or Mapbox API for plotting coordinates and routes.
* **Data Layer:** JSON structures representing simulated IoT sensor and camera data.
* **LLM Engine:** Gemini or OpenAI API to power the RAG Protocol Agent's safety instructions.

## 6. Core Data Entities

The system relies on a central node structure representing the state of each dustbin via the backend API:

```json
{
  "node_id": "BIN_402",
  "location": { "lat": 12.9716, "lng": 77.5946 },
  "current_fill_percentage": 45,
  "time_to_next_cycle_hrs": 24.0,
  "predicted_overflow_hrs": 14.5,
  "hazard_detected": false,
  "hazard_classification": null,
  "collection_required": true,
  "collection_reason": "PREDICTIVE_OVERFLOW"
}

```

*(Note: If `hazard_detected` is true, the `status_color` on the frontend should immediately override to Purple).*

## 7. Success Criteria for Hackathon MVP

* The map successfully renders nodes and updates dynamically based on the mocked API data.
* The TSP routing algorithm successfully filters out unnecessary nodes (Green) and routes efficiently between Red, Blue, and Purple nodes.
* The UI clearly distinguishes between a standard full bin and a "Proactive Pickup" bin.
* The RAG agent successfully generates coherent, accurate safety instructions based on the injected hazard type and Indian legal contexts.