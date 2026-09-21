import { create } from 'zustand';

interface AppState {
  selectedDistrict: string | null;
  season: 'monsoon' | 'dry' | 'winter';
  activeLayer: string | null;
  setSelectedDistrict: (district: string | null) => void;
  setSeason: (season: 'monsoon' | 'dry' | 'winter') => void;
  setActiveLayer: (layer: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedDistrict: null,
  season: 'dry',
  activeLayer: null,
  setSelectedDistrict: (selectedDistrict) => set({ selectedDistrict }),
  setSeason: (season) => set({ season }),
  setActiveLayer: (activeLayer) => set({ activeLayer }),
}));
