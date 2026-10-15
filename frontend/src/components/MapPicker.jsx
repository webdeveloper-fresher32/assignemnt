import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Crosshair, Map as MapIcon } from 'lucide-react';

// Fix Leaflet's default marker icon issue with bundlers
const customMarkerIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Helper component to smoothly center map when coordinates change externally
function MapCenterController({ center }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom(), { animate: true });
  }, [center, map]);
  return null;
}

// Map event handler for click-to-pin
function MapClickHandler({ onLocationSelect }) {
  useMapEvents({
    click(e) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function MapPicker({ latitude, longitude, regionName, onLocationSelect }) {
  const position = [latitude, longitude];

  return (
    <div className="map-picker-card glass-panel">
      <div className="map-header">
        <div className="map-title">
          <MapIcon size={16} className="text-orange" />
          <span>Interactive Climate Map</span>
        </div>
        <div className="map-instructions">
          <Crosshair size={14} />
          <span>Click anywhere to analyze coordinates</span>
        </div>
      </div>

      <div className="map-canvas-wrapper">
        <MapContainer
          center={position}
          zoom={5}
          scrollWheelZoom={false}
          className="leaflet-wrapper"
        >
          {/* CartoDB Dark Matter / Voyager tile layer for sleek dark aesthetics */}
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
          <MapCenterController center={position} />
          <MapClickHandler onLocationSelect={onLocationSelect} />
          <Marker position={position} icon={customMarkerIcon}>
            <Popup>
              <div className="marker-popup">
                <strong>{regionName}</strong>
                <div>Lat: {latitude.toFixed(4)}°</div>
                <div>Lon: {longitude.toFixed(4)}°</div>
              </div>
            </Popup>
          </Marker>
        </MapContainer>

        {/* HUD Coordinate Badge */}
        <div className="map-hud-badge">
          <span>{regionName}</span>
          <span className="hud-coords">{latitude.toFixed(3)}°N, {longitude.toFixed(3)}°E</span>
        </div>
      </div>
    </div>
  );
}
