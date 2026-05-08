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
