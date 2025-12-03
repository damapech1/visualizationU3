-- init.sql (versión correcta y definitiva)
DROP TABLE IF EXISTS raw_weather_events;

CREATE TABLE raw_weather_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(50) UNIQUE,
    city_id INT,
    city VARCHAR(100),
    region VARCHAR(50),
    segment VARCHAR(50),
    latitude FLOAT,
    longitude FLOAT,
    temperature_2m FLOAT,
    relative_humidity_2m FLOAT,
    apparent_temperature FLOAT,
    is_day BOOLEAN,
    precipitation_mm FLOAT,
    weather_code INT,
    cloud_cover INT,
    wind_speed_kmh FLOAT,
    raw_json JSONB,
    captured_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_city ON raw_weather_events(city);
CREATE INDEX IF NOT EXISTS idx_region ON raw_weather_events(region);