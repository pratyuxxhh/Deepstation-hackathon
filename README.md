# ClearGrid — Smart Waste Orchestration Dashboard

ClearGrid is a hackathon MVP for a multi-agent municipal waste collection system. It combines simulated IoT bin data, predictive overflow forecasting, route optimization, and hazard protocol generation into a single web dashboard.

## What this project does

- Shows a live map of Bengaluru Ward 68-style dustbins.
- Color-codes bins by condition:
  - `GREEN`: safe / ignore
  - `RED`: currently full and needs pickup
  - `BLUE`: predicted to overflow before the next scheduled service
  - `PURPLE`: hazardous material detected
- Filters out unnecessary stops and builds an optimized route using a nearest-neighbor TSP heuristic.
- Provides a HazMat safety brief when a hazardous bin is selected.

## Key features

- Backend: Python + FastAPI
- Frontend: React + Vite + TypeScript
- Map: Leaflet.js
- State: Zustand
- Routing: Haversine distance + nearest neighbor greedy TSP
- HazMat safety guidance: RAG-style prompt generation using local regulation text

## Architecture

### Agents

1. **Vision Agent** (precomputed in mock data)
   - Provides current fill level, hazard detection, and status color.
2. **Forecaster**
   - Marks bins as `BLUE` if predicted overflow happens before the next collection cycle.
3. **Dispatcher**
   - Builds a route through `RED`, `BLUE`, and `PURPLE` bins only.
4. **HazMat Protocol Agent**
   - Generates context-aware safety instructions for hazardous bins.

### API endpoints

- `GET /health` — service health check
- `GET /api/v1/bins` — returns all simulated bins
- `GET /api/v1/route` — returns the optimized route for required stops
- `GET /api/v1/hazmat/{node_id}` — returns a HazMat brief for the requested bin

## Project structure

```
cleargrid/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── agents/
│   │   ├── vision_agent.py
│   │   ├── forecaster.py
│   │   ├── dispatcher.py
│   │   └── hazmat_agent.py
│   ├── data/
│   │   ├── mock_bins.json
│   │   └── regulations/
│   │       ├── cpcb_guidelines.txt
│   │       ├── osh_code_2020.txt
│   │       └── solid_waste_management_rules_2016.txt
│   └── routers/
│       ├── bins.py
│       ├── route.py
│       └── hazmat.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts
    └── src/
        ├── App.tsx
        ├── index.css
        ├── main.tsx
        ├── components/
        │   ├── HazMatHUD/HazMatHUD.tsx
        │   ├── Map/GridMap.tsx
        │   └── RoutePanel/RoutePanel.tsx
        ├── lib/api.ts
        ├── store/index.ts
        └── types/index.ts
```

## Installation

### Backend

1. Open a terminal and navigate to `cleargrid/backend`
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### Frontend

1. Open a second terminal and navigate to `cleargrid/frontend`
2. Install dependencies:
   ```powershell
   npm install
   ```

## Running the app

### Start backend

```powershell
cd cleargrid/backend
uvicorn main:app --reload --port 8000
```

### Start frontend

```powershell
cd cleargrid/frontend
npm run dev
```

Then open the local Vite URL shown in the terminal (usually `http://localhost:5173`).

## How it works

### Bin states

Each bin object includes:
- `node_id`
- `location` (`lat`, `lng`)
- `current_fill_percentage`
- `time_to_next_cycle_hrs`
- `predicted_overflow_hrs`
- `hazard_detected`
- `hazard_classification`
- `collection_required`
- `collection_reason`
- `status_color`

### Route optimization

The backend builds an optimized route from the depot at `12.9352, 77.5947` and visits only required bins:
- `RED` bins: full
- `BLUE` bins: predictive overflow
- `PURPLE` bins: hazards

### HazMat handling

Selecting a `PURPLE` bin calls the HazMat endpoint, which loads regulation text from `backend/data/regulations` and returns a safety brief with:
- required PPE
- handling procedure
- reroute guidance if needed
- regulation citations

## Demo validation

Try these commands after the backend is running:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/bins | python -m json.tool
curl http://localhost:8000/api/v1/route | python -m json.tool
curl http://localhost:8000/api/v1/hazmat/BIN_219 | python -m json.tool
```

## Notes

- The frontend uses a dark dashboard theme and Leaflet-based map markers.
- The repository is designed as a hackathon MVP with simulated data and local rule files.
- Hazardous bins always override other statuses and display as `PURPLE`.

## License

This project is provided for hackathon/demo use.
