# ClearGrid — Master Architecture PRD
**For AI-Assisted Development (Cursor / Windsurf)**
**Version:** 1.0 | **Type:** Hackathon MVP

---

## Project Summary

ClearGrid is a multi-agent waste orchestration platform that transforms static municipal garbage collection into a dynamic, proactive digital grid. It deploys four specialized AI agents to eliminate route inefficiencies, prevent bin overflows, and handle hazardous waste autonomously.

**Demo perspective:** A municipal garbage truck driver's daily dashboard.

---

## Monorepo Structure

```
cleargrid/
├── frontend/                  # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/           # Leaflet map + bin nodes
│   │   │   ├── RoutePanel/    # Optimized route list
│   │   │   ├── HazMatHUD/     # Hazard alert overlay
│   │   │   └── Dashboard/     # Main layout shell
│   │   ├── hooks/             # useAgentPolling, useRouteData
│   │   ├── store/             # Zustand global state
│   │   ├── lib/               # API client
│   │   └── App.tsx
│   └── package.json
│
├── backend/                   # Python FastAPI
│   ├── main.py
│   ├── agents/
│   │   ├── vision_agent.py    # Agent 1: Fill level + hazard detection
│   │   ├── forecaster.py      # Agent 2: Overflow prediction
│   │   ├── dispatcher.py      # Agent 3: TSP route optimizer
│   │   └── hazmat_agent.py    # Agent 4: RAG safety protocol
│   ├── data/
│   │   ├── mock_bins.json     # Simulated IoT bin data
│   │   └── regulations/       # OSH Code, CPCB text files for RAG
│   ├── routers/
│   │   ├── bins.py
│   │   ├── route.py
│   │   └── hazmat.py
│   └── requirements.txt
│
└── README.md
```

---

## Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Frontend Framework | React 18 + Vite | TypeScript |
| Styling | Tailwind CSS v3 | Dark theme by default |
| Map | react-leaflet + Leaflet.js | OpenStreetMap tiles |
| State Management | Zustand | |
| Backend | Python 3.11 + FastAPI | |
| LLM / RAG | Claude API (`claude-sonnet-4-20250514`) | For HazMat agent |
| Routing Algorithm | Custom TSP (nearest neighbor heuristic) | Python |
| Data | JSON mock files | Simulated IoT sensors |
| Dev Server | Vite (frontend), Uvicorn (backend) | CORS enabled |

---

## Core Data Contract

All agents share this bin node schema. The frontend derives visual state from it.

```typescript
// frontend/src/types/index.ts

export type BinStatus = 'GREEN' | 'RED' | 'BLUE' | 'PURPLE';
export type CollectionReason = 'FULL' | 'PREDICTIVE_OVERFLOW' | 'HAZMAT' | null;

export interface BinNode {
  node_id: string;               // e.g. "BIN_402"
  location: {
    lat: number;
    lng: number;
  };
  current_fill_percentage: number;  // 0–100
  time_to_next_cycle_hrs: number;   // hours until scheduled truck visit
  predicted_overflow_hrs: number;   // hours until predicted overflow
  hazard_detected: boolean;
  hazard_classification: string | null;  // e.g. "Exposed Lithium Battery"
  collection_required: boolean;
  collection_reason: CollectionReason;
  status_color: BinStatus;  // computed by backend
}

export interface Route {
  waypoints: BinNode[];          // ordered list of required stops
  total_distance_km: number;
  polyline: [number, number][];  // [[lat, lng], ...] for map rendering
  depot: { lat: number; lng: number };
}

export interface HazMatBrief {
  node_id: string;
  hazard_type: string;
  safety_instructions: string;   // RAG-generated Markdown
  regulation_citations: string[];
  reroute_required: boolean;
  disposal_facility: { lat: number; lng: number; name: string } | null;
}
```

---

## Status Color Logic (Backend Computed)

```python
# backend/agents/vision_agent.py

def compute_status_color(bin: dict) -> str:
    if bin["hazard_detected"]:
        return "PURPLE"
    if bin["current_fill_percentage"] >= 80:
        return "RED"
    if bin["collection_required"] and bin["collection_reason"] == "PREDICTIVE_OVERFLOW":
        return "BLUE"
    return "GREEN"
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/bins` | Returns all bin nodes with computed status |
| GET | `/route` | Returns TSP-optimized route (RED + BLUE + PURPLE nodes) |
| GET | `/hazmat/{node_id}` | Triggers RAG agent, returns HazMat brief |
| POST | `/bins/simulate` | Dev only — regenerate mock data |

---

## Environment Variables

```bash
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...

# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## Agent Interaction Flow

```
[Mock IoT JSON]
      │
      ▼
[Agent 1: Vision]  ──►  fill_percentage + hazard_detected
      │
      ▼
[Agent 2: Forecaster]  ──►  predicted_overflow_hrs → flags BLUE bins
      │
      ▼
[Agent 3: Dispatcher]  ──►  filters GREEN, solves TSP on RED+BLUE+PURPLE
      │                      returns ordered Route
      ▼
[Agent 4: HazMat]      ──►  triggered on-demand when driver taps PURPLE node
      │                      queries RAG → returns safety brief
      ▼
[Frontend Dashboard]   ──►  renders map, route polyline, HazMat HUD
```

---

## Development Phases (Hackathon)

**Phase 1 (30 min):** Project scaffold, monorepo setup, mock data, API skeleton
**Phase 2 (60 min):** Backend agents (Vision + Forecaster + Dispatcher), `/bins` and `/route` endpoints
**Phase 3 (60 min):** Frontend map with color-coded nodes + route polyline
**Phase 4 (45 min):** HazMat RAG agent + HUD modal on frontend
**Phase 5 (15 min):** Polish, demo script, README

---

## Mock Data Seed

The system uses 20 simulated bins in Bengaluru Ward 68 area. See `PRD_02_MOCK_DATA.md` for the complete seed JSON.
