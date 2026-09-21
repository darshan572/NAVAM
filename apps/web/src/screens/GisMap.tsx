import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '@/store/useAppStore';

export const GisMap: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const { t } = useTranslation();
  const season = useAppStore(state => state.season);

  useEffect(() => {
    if (map.current) return; // initialize map only once
    if (!mapContainer.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: {
        version: 8,
        sources: {
          osm: {
            type: 'raster',
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: '© OpenStreetMap contributors',
          },
          martin: {
            type: 'vector',
            url: 'http://localhost:3000/public.habitations.json', // Adjust to actual martin endpoint
          }
        },
        layers: [
          {
            id: 'osm-tiles',
            type: 'raster',
            source: 'osm',
            minzoom: 0,
            maxzoom: 19
          },
        ]
      },
      center: [78.9629, 20.5937], // Center of India
      zoom: 4
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
  }, []);

  // Effect to update map layers based on season could go here
  useEffect(() => {
    if (map.current && map.current.isStyleLoaded()) {
      // update map style based on season
      console.log(`Season changed to ${season}, updating map layer...`);
    }
  }, [season]);

  return (
    <div className="flex flex-col h-full space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">{t('nav.gisMap')}</h1>
        <div className="bg-white px-4 py-2 rounded shadow-sm">
          <span className="text-sm text-gray-500">Vector Tiles:</span> 
          <span className="ml-2 font-medium">http://localhost:3000</span>
        </div>
      </div>
      
      <div className="flex-1 rounded-lg overflow-hidden border shadow-sm relative">
        <div ref={mapContainer} className="absolute inset-0" />
      </div>
    </div>
  );
};
