import { Flame, CloudRain, SunMedium, Moon, Sun, ShieldCheck, Activity, Code2, ExternalLink } from 'lucide-react';

export default function Navbar({ theme, setTheme, apiHealth, cachedStatus, executionTime }) {
  const toggleTheme = () => {
    const nextTheme = theme === 'dark' ? 'light' : 'dark';
    setTheme(nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  };

  return (
    <header className="navbar glass-panel">
      <div className="navbar-left">
        <div className="logo-badge">
          <Flame className="logo-icon" size={24} />
        </div>
        <div className="logo-text">
          <h1 className="logo-title">Climate Hazard Trend Analyzer</h1>
          <span className="logo-subtitle">Dygnify Ventures • Historical Climate Analytics</span>
        </div>
      </div>

      <div className="navbar-right">
        {/* API & Cache Health Badge */}
        <div className="health-badge" title={apiHealth ? `Backend Online (${apiHealth.database?.store_type || 'NoSQL'})` : 'Connecting to API...'}>
          <span className={`status-dot ${apiHealth ? 'online' : 'checking'}`}></span>
          <span className="health-text">
            {apiHealth ? 'API Live' : 'Connecting...'}
          </span>
          {executionTime !== null && (
            <span className="perf-badge">
              {cachedStatus ? '⚡ NoSQL Cache' : '🌐 ERA5 API'} ({executionTime}ms)
            </span>
          )}
        </div>

        {/* Theme Toggle */}
        <button 
          className="icon-btn" 
          onClick={toggleTheme} 
          aria-label="Toggle theme"
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} Mode`}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {/* External Link */}
        <a 
          href="https://github.com" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="icon-btn" 
          title="Source Code"
        >
          <Code2 size={18} />
        </a>
      </div>
    </header>
  );
}
