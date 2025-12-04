import os, json, psycopg2, sys, time
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

# Batch mode settings
batch_mode = "--batch" in sys.argv
no_message_count = 0
max_no_message_retries = 30 # Wait up to 30 seconds for messages

while True:
    msg = c.poll(1.0)
    
    if msg is None:
        if batch_mode:
            no_message_count += 1
            print(f"Batch mode: Esperando mensajes... ({no_message_count}/{max_no_message_retries})")
            if no_message_count >= max_no_message_retries:
                print("Batch mode: Timeout alcanzado sin nuevos mensajes. Finalizando.")
                break
        continue
    
    # Reset counter if we got a message
    if batch_mode:
        no_message_count = 0

    if msg.error():
        print(msg.error())
        continue

    data = json.loads(msg.value())

    try:
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
    except Exception as e:
        print(f"Error insertando en BD: {e}")
        conn.rollback()