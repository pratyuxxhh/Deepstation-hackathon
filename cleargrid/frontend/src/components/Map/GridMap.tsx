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
      {bins.map((bin: BinNode) => (
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
