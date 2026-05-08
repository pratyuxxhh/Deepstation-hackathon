# PRD 04 — Frontend Dashboard (React + Leaflet)
**Directory:** `frontend/src/`

---

## Objective

Build the driver-facing command center dashboard. A dark-themed, map-centric interface showing all bin nodes color-coded by status, a TSP-optimized route polyline, a side panel with the stop list, and a HazMat HUD modal that appears when a PURPLE node is tapped.

---

## Tech Stack (Frontend)

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install tailwindcss @tailwindcss/vite leaflet react-leaflet zustand axios react-markdown
```

---

## Layout Spec

```
┌─────────────────────────────────────────────────────────┐
│  ClearGrid  [Ward 68]    🟢 8  🔴 4  🔵 4  🟣 4  [12 stops] │  ← Header
├──────────────────────┬──────────────────────────────────┤
│                      │  TODAY'S ROUTE                   │
│                      │  ──────────────────────          │
│   LEAFLET MAP        │  Stop 1  🟣 BIN_219              │
│   (full height)      │  ⚠️ Lithium Battery              │
│                      │  ──────────────────────          │
│   Nodes as           │  Stop 2  🔴 BIN_317              │
│   circle markers     │  88% full                        │
│                      │  ──────────────────────          │
│   Route polyline     │  Stop 3  🔵 BIN_402              │
│   connecting stops   │  Overflow in 14.5h               │
│                      │  ──────────────────────          │
│                      │  14.7 km total                   │
└──────────────────────┴──────────────────────────────────┘
│  🟢 Empty  🔴 Full  🔵 Predictive  🟣 Hazmat            │  ← Legend
└─────────────────────────────────────────────────────────┘
```

When a PURPLE node is clicked: full-screen modal HazMat HUD overlays the map.

---

## Color System

| Status | Hex | Tailwind | Map Marker Color |
|---|---|---|---|
| GREEN | `#22c55e` | `text-green-500` | `#22c55e` |
| RED | `#ef4444` | `text-red-500` | `#ef4444` |
| BLUE | `#3b82f6` | `text-blue-500` | `#3b82f6` |
| PURPLE | `#a855f7` | `text-purple-500` | `#a855f7` (pulse animation) |

Background: `#0f172a` (slate-900)
Panel: `#1e293b` (slate-800)
Text primary: `#f1f5f9` (slate-100)
Text secondary: `#94a3b8` (slate-400)

---

## Task 1: Zustand Store

**File:** `frontend/src/store/index.ts`

```typescript
import { create } from 'zustand';
import type { BinNode, Route, HazMatBrief } from '../types';

interface AppState {
  bins: BinNode[];
  route: Route | null;
  selectedBin: BinNode | null;
  hazmatBrief: HazMatBrief | null;
  hazmatLoading: boolean;
  
  setBins: (bins: BinNode[]) => void;
  setRoute: (route: Route) => void;
  selectBin: (bin: BinNode | null) => void;
  setHazmatBrief: (brief: HazMatBrief | null) => void;
  setHazmatLoading: (loading: boolean) => void;
}

export const useStore = create<AppState>((set) => ({
  bins: [],
  route: null,
  selectedBin: null,
  hazmatBrief: null,
  hazmatLoading: false,
  
  setBins: (bins) => set({ bins }),
  setRoute: (route) => set({ route }),
  selectBin: (bin) => set({ selectedBin: bin, hazmatBrief: null }),
  setHazmatBrief: (brief) => set({ hazmatBrief: brief }),
  setHazmatLoading: (loading) => set({ hazmatLoading: loading }),
}));
```

---

## Task 2: API Client

**File:** `frontend/src/lib/api.ts`

```typescript
import axios from 'axios';
import type { BinNode, Route, HazMatBrief } from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
});

export const fetchBins = (): Promise<BinNode[]> =>
  api.get('/bins').then(r => r.data);

export const fetchRoute = (): Promise<Route> =>
  api.get('/route').then(r => r.data);

export const fetchHazmat = (nodeId: string): Promise<HazMatBrief> =>
  api.get(`/hazmat/${nodeId}`).then(r => r.data);
```

---

## Task 3: Map Component

**File:** `frontend/src/components/Map/GridMap.tsx`

```typescript
import { MapContainer, TileLayer, CircleMarker, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useStore } from '../../store';
import type { BinNode } from '../../types';

const STATUS_COLORS: Record<string, string> = {
  GREEN: '#22c55e',
  RED: '#ef4444',
  BLUE: '#3b82f6',
  PURPLE: '#a855f7',
};

const DEPOT_COORDS: [number, number] = [12.9352, 77.5947];

export function GridMap() {
  const { bins, route, selectedBin, selectBin } = useStore();

  return (
    <MapContainer
      center={[12.9500, 77.6000]}
      zoom={13}
      className="h-full w-full"
      style={{ background: '#0f172a' }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='CartoDB'
      />
      
      {/* Route polyline */}
      {route?.polyline && (
        <Polyline
          positions={route.polyline as [number, number][]}
          color="#6366f1"
          weight={3}
          opacity={0.8}
          dashArray="8 4"
        />
      )}
      
      {/* Depot marker */}
      <CircleMarker
        center={DEPOT_COORDS}
        radius={10}
        pathOptions={{ fillColor: '#f59e0b', color: '#fbbf24', fillOpacity: 1 }}
      >
        <Tooltip permanent>🚛 Depot</Tooltip>
      </CircleMarker>
      
      {/* Bin nodes */}
      {bins.map((bin) => (
        <CircleMarker
          key={bin.node_id}
          center={[bin.location.lat, bin.location.lng]}
          radius={bin.status_color === 'PURPLE' ? 12 : 9}
          pathOptions={{
            fillColor: STATUS_COLORS[bin.status_color],
            color: bin.node_id === selectedBin?.node_id ? '#ffffff' : STATUS_COLORS[bin.status_color],
            weight: bin.node_id === selectedBin?.node_id ? 3 : 1.5,
            fillOpacity: 0.9,
          }}
          eventHandlers={{
            click: () => selectBin(bin),
          }}
        >
          <Tooltip>
            <div>
              <strong>{bin.node_id}</strong><br />
              {bin.current_fill_percentage}% full<br />
              {bin.hazard_classification ?? bin.collection_reason ?? 'No action needed'}
            </div>
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
```

---

## Task 4: Route Panel (Sidebar)

**File:** `frontend/src/components/RoutePanel/RoutePanel.tsx`

```typescript
import { useStore } from '../../store';
import { fetchHazmat } from '../../lib/api';

const STATUS_EMOJI: Record<string, string> = {
  RED: '🔴', BLUE: '🔵', PURPLE: '🟣', GREEN: '🟢',
};

export function RoutePanel() {
  const { route, selectBin, setHazmatBrief, setHazmatLoading } = useStore();

  const handleStopClick = async (bin: any) => {
    selectBin(bin);
    if (bin.status_color === 'PURPLE') {
      setHazmatLoading(true);
      try {
        const brief = await fetchHazmat(bin.node_id);
        setHazmatBrief(brief);
      } finally {
        setHazmatLoading(false);
      }
    }
  };

  if (!route) {
    return (
      <div className="p-4 text-slate-400 text-sm">
        Loading optimized route...
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-slate-800 text-slate-100">
      <div className="p-4 border-b border-slate-700">
        <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Today's Route
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          {route.waypoints.length} stops · {route.total_distance_km} km
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {route.waypoints.map((bin, index) => (
          <button
            key={bin.node_id}
            onClick={() => handleStopClick(bin)}
            className="w-full text-left px-4 py-3 border-b border-slate-700 hover:bg-slate-700 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500 w-6">{index + 1}</span>
              <span>{STATUS_EMOJI[bin.status_color]}</span>
              <span className="font-mono text-sm font-medium">{bin.node_id}</span>
              {bin.status_color === 'PURPLE' && (
                <span className="ml-auto text-xs bg-purple-900 text-purple-300 px-2 py-0.5 rounded-full">
                  HAZMAT
                </span>
              )}
            </div>
            <div className="ml-8 text-xs text-slate-400 mt-0.5">
              {bin.status_color === 'PURPLE'
                ? bin.hazard_classification
                : bin.status_color === 'BLUE'
                ? `Overflow in ${bin.predicted_overflow_hrs}h`
                : `${bin.current_fill_percentage}% full`
              }
            </div>
          </button>
        ))}
      </div>
      
      <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
        {route.skipped_count} green bins skipped
      </div>
    </div>
  );
}
```

---

## Task 5: HazMat HUD Modal

**File:** `frontend/src/components/HazMatHUD/HazMatHUD.tsx`

```typescript
import ReactMarkdown from 'react-markdown';
import { useStore } from '../../store';

export function HazMatHUD() {
  const { selectedBin, hazmatBrief, hazmatLoading, selectBin } = useStore();
  
  if (!selectedBin || selectedBin.status_color !== 'PURPLE') return null;

  return (
    <div className="absolute inset-0 z-50 flex items-end md:items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="bg-slate-900 border border-purple-500/50 rounded-2xl w-full max-w-lg max-h-[85vh] overflow-hidden shadow-2xl shadow-purple-900/30">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-purple-500/30 bg-purple-950/50">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-lg">⚠️</span>
              <h3 className="font-semibold text-purple-200">HazMat Alert</h3>
            </div>
            <p className="text-xs text-purple-400 mt-0.5">
              {selectedBin.node_id} · {selectedBin.hazard_classification}
            </p>
          </div>
          <button
            onClick={() => selectBin(null)}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-700 transition-colors"
          >
            ✕
          </button>
        </div>
        
        {/* Content */}
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {hazmatLoading ? (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-400 text-sm">Retrieving safety protocol...</p>
              <p className="text-slate-500 text-xs">Querying OSH Code + CPCB guidelines</p>
            </div>
          ) : hazmatBrief ? (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{hazmatBrief.safety_instructions}</ReactMarkdown>
              
              {hazmatBrief.disposal_facility && (
                <div className="mt-4 p-3 bg-amber-950/50 border border-amber-500/30 rounded-lg">
                  <p className="text-amber-300 text-xs font-semibold uppercase tracking-wider mb-1">
                    Route Updated
                  </p>
                  <p className="text-amber-200 text-sm">
                    🏭 {hazmatBrief.disposal_facility.name}
                  </p>
                  <p className="text-amber-400 text-xs mt-0.5">
                    {hazmatBrief.disposal_facility.address}
                  </p>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
```

---

## Task 6: App Root + Data Initialization

**File:** `frontend/src/App.tsx`

```typescript
import { useEffect } from 'react';
import { GridMap } from './components/Map/GridMap';
import { RoutePanel } from './components/RoutePanel/RoutePanel';
import { HazMatHUD } from './components/HazMatHUD/HazMatHUD';
import { useStore } from './store';
import { fetchBins, fetchRoute } from './lib/api';

const STATUS_COUNTS = (bins: any[]) => ({
  green: bins.filter(b => b.status_color === 'GREEN').length,
  red: bins.filter(b => b.status_color === 'RED').length,
  blue: bins.filter(b => b.status_color === 'BLUE').length,
  purple: bins.filter(b => b.status_color === 'PURPLE').length,
});

export default function App() {
  const { setBins, setRoute, bins, route } = useStore();

  useEffect(() => {
    Promise.all([fetchBins(), fetchRoute()]).then(([bins, route]) => {
      setBins(bins);
      setRoute(route);
    });
  }, []);

  const counts = STATUS_COUNTS(bins);

  return (
    <div className="h-screen flex flex-col bg-slate-900 text-slate-100 font-mono">
      
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2.5 bg-slate-800 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-green-400 font-bold text-sm tracking-widest">CLEARGRID</span>
          <span className="text-slate-500 text-xs">Ward 68 · Live</span>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-green-400">🟢 {counts.green}</span>
          <span className="text-red-400">🔴 {counts.red}</span>
          <span className="text-blue-400">🔵 {counts.blue}</span>
          <span className="text-purple-400">🟣 {counts.purple}</span>
          {route && (
            <span className="text-slate-400 ml-2">{route.waypoints.length} stops</span>
          )}
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className="flex-1 relative">
          <GridMap />
          <HazMatHUD />
        </div>
        
        {/* Sidebar */}
        <div className="w-72 shrink-0 border-l border-slate-700 overflow-hidden">
          <RoutePanel />
        </div>
      </div>

      {/* Legend */}
      <footer className="flex items-center gap-4 px-4 py-2 bg-slate-800 border-t border-slate-700 text-xs text-slate-400 shrink-0">
        <span>🟢 Empty — skip</span>
        <span>🔴 Full — collect now</span>
        <span>🔵 Predictive pickup</span>
        <span>🟣 Hazmat — tap for protocol</span>
      </footer>
    </div>
  );
}
```

---

## Acceptance Criteria

- [ ] Map renders in dark mode with CartoDB dark tiles
- [ ] All 20 bins appear as circle markers with correct status colors
- [ ] PURPLE markers are visually larger (radius 12 vs 9)
- [ ] Route polyline (dashed indigo) connects stops in correct TSP order
- [ ] Depot marker (amber) visible at starting location
- [ ] Sidebar lists all required stops (RED, BLUE, PURPLE only) in TSP order
- [ ] Clicking a PURPLE bin in the sidebar or map triggers HazMat HUD
- [ ] HazMat HUD shows loading spinner while fetching from API
- [ ] Safety brief renders as formatted Markdown inside the HUD
- [ ] Disposal facility address shown in amber alert box
- [ ] HUD dismisses on X button click
- [ ] Header shows correct bin counts by color
- [ ] App loads without console errors
