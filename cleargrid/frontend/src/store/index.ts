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
