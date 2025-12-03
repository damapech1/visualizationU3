import os, json, psycopg2
from confluent_kafka import Consumer
from dotenv import load_dotenv

load_dotenv()

c = Consumer({
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'group.id': 'postgres-group',
    'auto.offset.reset': 'earliest'
})
c.subscribe([os.getenv('KAFKA_TOPIC')])

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    dbname=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)
cur = conn.cursor()

print("Consumer → PostgreSQL iniciado")
while True:
    msg = c.poll(1.0)
    if msg is None: continue
    if msg.error():
        print(msg.error())
        continue

    data = json.loads(msg.value())

    cur.execute("""
        INSERT INTO raw_weather_events (
            event_id, city_id, city, region, segment, latitude, longitude,
            temperature_2m, relative_humidity_2m, apparent_temperature,
            is_day, precipitation_mm, weather_code, cloud_cover,
            wind_speed_kmh, raw_json
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (event_id) DO NOTHING
    """, (
        data['event_id'], data['city_id'], data['city'], data['region'], data['segment'],
        data['latitude'], data['longitude'], data['temperature_2m'], data['relative_humidity_2m'],
        data['apparent_temperature'], data['is_day'], data['precipitation_mm'],
        data['weather_code'], data['cloud_cover'], data['wind_speed_kmh'], json.dumps(data)
    ))
    conn.commit()
    print(f"Insertado → {data['city']} {data['temperature_2m']}°C")