-- Create analytics table if it doesn't exist
CREATE TABLE IF NOT EXISTS analytics_weather (
    analytics_id SERIAL PRIMARY KEY,
    city VARCHAR(100) UNIQUE,
    avg_temperature FLOAT,
    max_temperature FLOAT,
    min_temperature FLOAT,
    avg_humidity FLOAT,
    total_precipitation FLOAT,
    record_count INT,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Transform and Load logic (Upsert based on city)
INSERT INTO analytics_weather (city, avg_temperature, max_temperature, min_temperature, avg_humidity, total_precipitation, record_count, last_updated)
SELECT 
    city,
    AVG(temperature_2m) as avg_temperature,
    MAX(temperature_2m) as max_temperature,
    MIN(temperature_2m) as min_temperature,
    AVG(relative_humidity_2m) as avg_humidity,
    SUM(precipitation_mm) as total_precipitation,
    COUNT(*) as record_count,
    NOW() as last_updated
FROM raw_weather_events
GROUP BY city
ON CONFLICT (city) 
DO UPDATE SET
    avg_temperature = EXCLUDED.avg_temperature,
    max_temperature = EXCLUDED.max_temperature,
    min_temperature = EXCLUDED.min_temperature,
    avg_humidity = EXCLUDED.avg_humidity,
    total_precipitation = EXCLUDED.total_precipitation,
    record_count = EXCLUDED.record_count,
    last_updated = NOW();

-- Note: The above logic is a simple aggregation. 
-- In a real scenario, you might want to aggregate by day/hour or append new daily stats instead of overwriting by city.
-- For this assignment, we are creating a summary table for the dashboard.
