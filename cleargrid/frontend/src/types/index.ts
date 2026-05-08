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
