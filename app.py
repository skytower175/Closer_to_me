import React, { useState, useEffect } from 'react';

const GeoLocationApp = () => {
  const [location, setLocation] = useState({
    loaded: false,
    coordinates: { lat: null, lng: null },
  });
  const [error, setError] = useState(null);
  const [isWatching, setIsWatching] = useState(false);
  let watchId = null;

  // Success handler for geolocation API
  const onSuccess = (position) => {
    setLocation({
      loaded: true,
      coordinates: {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      },
    });
  };

  // Error handler for geolocation API
  const onError = (err) => {
    setError({
      code: err.code,
      message: err.message,
    });
  };

  // Get current position
  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError({
        message: "Geolocation is not supported by your browser",
      });
      return;
    }

    navigator.geolocation.getCurrentPosition(onSuccess, onError);
  };

  // Toggle continuous position watching
  const toggleWatchLocation = () => {
    if (isWatching) {
      navigator.geolocation.clearWatch(watchId);
    } else {
      watchId = navigator.geolocation.watchPosition(onSuccess, onError);
    }
    setIsWatching(!isWatching);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (watchId) navigator.geolocation.clearWatch(watchId);
    };
  }, []);

  return (
    <div className="geo-app">
      <h1>Geolocation Tracker</h1>
      
      <div className="controls">
        <button onClick={getCurrentLocation}>
          Get Current Location
        </button>
        
        <button onClick={toggleWatchLocation} className={isWatching ? 'active' : ''}>
          {isWatching ? 'Stop Tracking' : 'Start Tracking'}
        </button>
      </div>

      {!location.loaded && !error && (
        <div className="status">Waiting for location request...</div>
      )}

      {error && (
        <div className="error">
          Error {error.code}: {error.message}
        </div>
      )}

      {location.loaded && !error && (
        <div className="results">
          <h2>Your Position</h2>
          <ul>
            <li>Latitude: {location.coordinates.lat}</li>
            <li>Longitude: {location.coordinates.lng}</li>
          </ul>
          
          {/* Link to open in Google Maps */}
          <a
            href={`https://www.google.com/maps/search/?api=1&query=${location.coordinates.lat},${location.coordinates.lng}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            View on Google Maps
          </a>
        </div>
      )}
    </div>
  );
};

export default GeoLocationApp;