import React, { useEffect, useState, useRef } from 'react';
import './App.css';

export default function DayMate() {
  const [location, setLocation] = useState(() => {
    const saved = localStorage.getItem('userLocation');
    if (saved) return saved;
    return 'Dhaka, BD';
  });

  const [tempLocation, setTempLocation] = useState(location);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [mapPreviewUrl, setMapPreviewUrl] = useState(null);

  const [weather, setWeather] = useState(null);
  const [hourly, setHourly] = useState([]);
  const [sevenDay, setSevenDay] = useState([]);
  const [aqi, setAqi] = useState(null);
  const [recommendation, setRecommendation] = useState('');
  const [news, setNews] = useState([]);

  const [now, setNow] = useState(new Date());
  const [loading, setLoading] = useState(false);

  const fetchInProgress = useRef(false);
  const currentLocationRef = useRef(location);

  // MOCK DATA
  const mockData = {
    weather: {
      current: { temp: 24, condition: 'Rainy', icon: 'rain', humidity: 65, wind: 12 },
      hourly: [
        { time: '2 PM', temp: 24, condition: 'Rain' },
        { time: '3 PM', temp: 23, condition: 'Rain' },
        { time: '4 PM', temp: 22, condition: 'Cloudy' },
        { time: '5 PM', temp: 21, condition: 'Cloudy' },
        { time: '6 PM', temp: 20, condition: 'Clear' },
        { time: '7 PM', temp: 19, condition: 'Clear' }
      ],
      daily7: [
        { day: 'Thu', date: 'Nov 27', high: 25, low: 17, condition: 'Rain' },
        { day: 'Fri', date: 'Nov 28', high: 23, low: 16, condition: 'Cloudy' },
        { day: 'Sat', date: 'Nov 29', high: 22, low: 15, condition: 'Cloudy' },
        { day: 'Sun', date: 'Nov 30', high: 24, low: 16, condition: 'Sunny' },
        { day: 'Mon', date: 'Dec 1', high: 26, low: 18, condition: 'Sunny' },
        { day: 'Tue', date: 'Dec 2', high: 24, low: 17, condition: 'Partly Cloudy' },
        { day: 'Wed', date: 'Dec 3', high: 22, low: 15, condition: 'Rain' }
      ]
    },
    news: [
      { title: '', url: '', date: '', image: '', source: '', logo: '' }
    ]
  };

  const cleanLocation = (loc) => {
  if (!loc) return "Dhaka, BD";
  return loc.trim();
};

const saveLocation = (loc) => {
  const cleaned = cleanLocation(loc);
  localStorage.setItem('userLocation', cleaned);
  setLocation(cleaned);
};


  // Load saved location
  useEffect(() => {
    const savedLocation = localStorage.getItem('userLocation');
    if (savedLocation) setLocation(cleanLocation(savedLocation));
  }, []);

  // FETCH DATA ONLY WHEN REAL LOCATION CHANGES
  useEffect(() => {
    const fetchAllData = async () => {
      const city = cleanLocation(location);

      if (fetchInProgress.current && currentLocationRef.current === city) return;

      fetchInProgress.current = true;
      currentLocationRef.current = city;
      setLoading(true);

      // Reset recommendation to animate loader
      setRecommendation("Loading..");

      try {
        const res = await fetch(`https://daymate-django.onrender.com/api/weather/${encodeURIComponent(city)}`);

        if (!res.ok) {
          setWeather(mockData.weather.current);
          setHourly(mockData.weather.hourly);
          setSevenDay(mockData.weather.daily7);
          setAqi(mockData.aqi);
          setRecommendation("Loading..");
          setNews(mockData.news);
        } else {
          const data = await res.json();

          setWeather(data.current || mockData.weather.current);
          setHourly(data.hourly || mockData.weather.hourly);
          setSevenDay(data.daily7 || mockData.weather.daily7);
          setAqi(data.aqi || mockData.aqi);

          setRecommendation(data.recommendation || "");

          if (data.news && data.news.length > 0) {
            setNews(
              data.news.map(item => ({
                title: item.title || '',
                url: item.url || '#',
                date: item.date || '',
                image: item.image || '',
                source: item.source || '',
                logo: item.logo || ''
              }))
            );
          } else {
            setNews(mockData.news);
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
        fetchInProgress.current = false;
      }
    };

    fetchAllData();
  }, [location]);

  // CLOCK
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60 * 1000);
    return () => clearInterval(id);
  }, []);

  // MAP PREVIEW
  useEffect(() => {
    const base = 'https://www.google.com/maps?q=';
    const q = encodeURIComponent(location || 'Dhaka, BD');
    setMapPreviewUrl(`${base}${q}&output=embed`);
  }, [location]);

  const useDeviceLocation = () => {
    if (!navigator.geolocation) return alert('Geolocation is not supported.');
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const coord = `${pos.coords.latitude.toFixed(4)},${pos.coords.longitude.toFixed(4)}`;
        setTempLocation(coord);
        saveLocation(coord);
        setShowLocationModal(false);
      },
      () => alert('Unable to get location.')
    );
  };

  return (
    <div className="app-container">
      <header className="top-banner">
        <div className="app-logo-center">
          <img src="https://cdn-icons-png.flaticon.com/512/3222/3222800.png" alt="sun" className="logo-sun" />
          <h1 className="app-title">DayMate</h1>
        </div>
      </header>

      <div className="main-container">
        {/* LEFT SIDEBAR */}
        <aside className="left-sidebar">
          <div className="map-preview-card">
            <h4 className="section-title-small">Map Preview</h4>

            {mapPreviewUrl ? (
              <div className="map-frame">
                <iframe title="map-preview" src={mapPreviewUrl} style={{ border: 0, width: '100%', height: '220px' }} loading="lazy" />
              </div>
            ) : (
              <div className="map-placeholder-small">Loading map...</div>
            )}

            <button
              className="btn-device small"
              onClick={() => {
                setTempLocation(location);
                setShowLocationModal(true);
              }}
            >
              Change Location
            </button>
          </div>

          <div className="location-box">
            <div className="location-header">
              <div className="location-label">
                <span className="location-icon">📍</span>
                <span>Location</span>
              </div>
              <button
                className="edit-btn"
                onClick={() => {
                  setTempLocation(location);
                  setShowLocationModal(true);
                }}
              >
                ✏️
              </button>
            </div>
            <p className="location-text">{location}</p>
          </div>

          <div className="time-card">
            <h4 className="section-title"><span className="title-icon">⏰</span> Date & Time</h4>
            <div className="time-content">
              <div className="time-now">{now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
              <div className="date-now">{now.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}</div>
            </div>
          </div>

          <div className="weather-card current-weather-card">
            <h4 className="section-title"><span className="title-icon">☁️</span> Current Weather</h4>
            <div className="weather-main new-layout">
              <div className="weather-image">
                <img src={weather?.icon || 'clear'} alt="weather" />
              </div>
              <div className="weather-temp-section">
                <div className="temp-large">{weather?.temp || 0}</div>
                <div className="weather-condition">{weather?.condition || '—'}</div>
              </div>
            </div>

            <div className="weather-details">
              <div className="weather-detail-item">
                <span className="detail-icon">༄</span>
                <div><div className="detail-label">Air Quality</div><div className="detail-value">{weather?.aqi || '—'}</div></div>
              </div>

              <div className="weather-detail-item">
                <span className="detail-icon">💨</span>
                <div><div className="detail-label">Wind</div><div className="detail-value">{weather?.wind || '—'}</div></div>
              </div>
            </div>
          </div>
        </aside>

        {/* MIDDLE SECTION */}
        <main className="middle-section">

          {/* AI Recommendation */}
          <div className="recommendation-card-hero">
            <img src={weather?.icon || 'clear'} alt="" className="recommendation-icon-img" />

            <div className="recommendation-content-hero">
              <div className="ai-label"><span>AI Recommendation</span></div>
              <h2>Your Smart Day Plan</h2>

              <p class="recommm">
                {recommendation}
              </p>
            </div>
          </div>

          {/* Hourly */}
          <div className="hourly-forecast">
            <h3 className="forecast-title">
              <span className="forecast-icon">☁️</span> Next 12 Hours
            </h3>

            <div className="hourly-grid">
              {(hourly.length ? hourly : mockData.weather.hourly).map((hour, idx) => (
                <div key={idx} className="hour-card">
                  <div className="hour-time">{hour.time}</div>
                  <img src={hour.condition} alt={hour.condition} className="hour-icon" />
                  <div className="hour-temp">{hour.temp}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Weekly */}
          <div className="weekly-forecast">
            <h3 className="forecast-title">
              <span className="forecast-icon">📅</span> Next 7 Days Weather Forecast
            </h3>

            <div className="weekly-grid">
              {(sevenDay.length ? sevenDay : mockData.weather.daily7).map((day, i) => (
                <div key={i} className="day-card">
                  <div className="day-header">
                    <div className="day-name">{day.day}</div>
                    <div className="day-date">{day.date}</div>
                  </div>
                  <img src={day.icon} alt={day.icon} className="day-icon" />
                  <div className="day-temps">
                    <div className="high">{day.high}</div>
                    <div className="low">{day.low}</div>
                  </div>
                  <div className="day-cond">{day.condition}</div>
                </div>
              ))}
            </div>
          </div>
        </main>

        {/* NEWS SIDEBAR */}
        <aside className="right-sidebar">
          <div className="news-header">
            <span className="news-icon">📰</span><h3>Local News</h3>
          </div>

          <div className="news-list">
            {(news.length ? news : mockData.news).map((item, idx) => (
              <div key={idx} className="news-card">
                <div className="news-image"><img src={item.image} alt={item.title} /></div>
                <div className="news-content">
                  <a href={item.url} target="_blank" rel="noopener noreferrer"><h4 className="news-title">{item.title}</h4></a>
                  <div className="news-source-row">
                    <div className="news-logo"><img src={item.logo} alt={`${item.source} logo`} /></div>
                    <div className="news-source">{item.source}</div>
                  </div>
                </div>
                <div className="news-time"><span>{item.date}</span></div>
              </div>
            ))}
          </div>
        </aside>
      </div>

      {/* LOCATION MODAL */}
      {showLocationModal && (
        <div className="modal-overlay" onClick={() => setShowLocationModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Select Your Location</h3>

            <div className="map-modal-preview">
              {mapPreviewUrl ? (
                <iframe title="map-modal" src={mapPreviewUrl} style={{ border: 0, width: '100%', height: '320px' }} loading="lazy" />
              ) : (
                <div className="map-placeholder">Interactive Map Preview</div>
              )}
            </div>

            <div className="modal-inputs">
              <input
                type="text"
                value={tempLocation}
                onChange={(e) => setTempLocation(e.target.value)}
                placeholder="Enter location..."
                className="location-input-modal"
              />

              <div className="modal-buttons">
                <button
                  onClick={() => {
                    saveLocation(tempLocation);
                    setShowLocationModal(false);
                  }}
                  className="btn-confirm"
                >
                  Confirm Location
                </button>
              </div>

              <button onClick={() => setShowLocationModal(false)} className="btn-cancel">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
