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
