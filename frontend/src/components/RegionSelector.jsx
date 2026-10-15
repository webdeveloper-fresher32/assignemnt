import React, { useState, useEffect, useRef } from 'react';
import { Search, MapPin, Globe, Loader2, Navigation } from 'lucide-react';
import { searchLocations } from '../services/api';

const PRESET_CITIES = [
  { name: 'New Delhi, India', lat: 28.6139, lon: 77.2090, flag: '🇮🇳' },
  { name: 'Phoenix, USA', lat: 33.4484, lon: -112.0740, flag: '🇺🇸' },
  { name: 'Madrid, Spain', lat: 40.4168, lon: -3.7038, flag: '🇪🇸' },
  { name: 'London, UK', lat: 51.5074, lon: -0.1278, flag: '🇬🇧' },
  { name: 'Tokyo, Japan', lat: 35.6762, lon: 139.6503, flag: '🇯🇵' },
  { name: 'Sydney, Australia', lat: -33.8688, lon: 151.2093, flag: '🇦🇺' },
  { name: 'Cairo, Egypt', lat: 30.0444, lon: 31.2357, flag: '🇪🇬' },
  { name: 'São Paulo, Brazil', lat: -23.5505, lon: -46.6333, flag: '🇧🇷' }
];

export default function RegionSelector({ latitude, longitude, regionName, onLocationChange }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on click outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced geocoding search
  useEffect(() => {
    if (!searchQuery || searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const results = await searchLocations(searchQuery);
        setSearchResults(results || []);
        setIsOpen(true);
      } catch (err) {
        console.error('Geocoding search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 350);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  const handleSelectResult = (loc) => {
    const displayName = `${loc.name}${loc.admin1 ? ', ' + loc.admin1 : ''}${loc.country ? ', ' + loc.country : ''}`;
    onLocationChange({
      latitude: loc.latitude,
      longitude: loc.longitude,
      regionName: displayName
    });
    setSearchQuery('');
    setIsOpen(false);
  };

  const handlePresetClick = (preset) => {
    onLocationChange({
      latitude: preset.lat,
      longitude: preset.lon,
      regionName: preset.name
    });
  };

  return (
    <div className="region-selector">
      <div className="section-label">
        <MapPin size={16} className="text-orange" />
        <span>Geographic Region</span>
      </div>

      {/* Search Input with Autocomplete */}
      <div className="search-container" ref={dropdownRef}>
        <div className="search-input-wrapper">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search any city or region globally (e.g. Paris, Chicago, Mumbai)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery.length >= 2 && setIsOpen(true)}
          />
          {isSearching && <Loader2 size={16} className="search-spinner" />}
        </div>

        {/* Dropdown Menu */}
        {isOpen && searchResults.length > 0 && (
          <ul className="search-dropdown glass-panel">
            {searchResults.map((loc) => (
              <li 
                key={loc.id} 
                className="dropdown-item"
                onClick={() => handleSelectResult(loc)}
              >
                <div className="item-name">
                  <strong>{loc.name}</strong>
                  <span className="item-details">
                    {[loc.admin1, loc.country].filter(Boolean).join(', ')}
                  </span>
                </div>
                <div className="item-coords">
                  {loc.latitude.toFixed(2)}°, {loc.longitude.toFixed(2)}°
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Preset Cities Pill Carousel */}
      <div className="presets-wrapper">
        <span className="presets-label">Popular Regions:</span>
        <div className="presets-list">
          {PRESET_CITIES.map((city) => {
            const isSelected = Math.abs(city.lat - latitude) < 0.05 && Math.abs(city.lon - longitude) < 0.05;
            return (
              <button
                key={city.name}
                type="button"
                className={`preset-pill ${isSelected ? 'active' : ''}`}
                onClick={() => handlePresetClick(city)}
              >
                <span className="preset-flag">{city.flag}</span>
                <span className="preset-name">{city.name.split(',')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom Coordinates Inputs */}
      <div className="coords-grid">
        <div className="coord-field">
          <label>Latitude (-90° to 90°)</label>
          <input
            type="number"
            step="0.0001"
            min="-90"
            max="90"
            value={latitude}
            onChange={(e) => onLocationChange({
              latitude: parseFloat(e.target.value) || 0,
              longitude,
              regionName: `Lat ${parseFloat(e.target.value) || 0}, Lon ${longitude}`
            })}
          />
        </div>
        <div className="coord-field">
          <label>Longitude (-180° to 180°)</label>
          <input
            type="number"
            step="0.0001"
            min="-180"
            max="180"
            value={longitude}
            onChange={(e) => onLocationChange({
              latitude,
              longitude: parseFloat(e.target.value) || 0,
              regionName: `Lat ${latitude}, Lon ${parseFloat(e.target.value) || 0}`
            })}
          />
        </div>
      </div>
    </div>
  );
}
