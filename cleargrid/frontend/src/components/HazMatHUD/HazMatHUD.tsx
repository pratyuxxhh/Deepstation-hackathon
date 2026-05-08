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
