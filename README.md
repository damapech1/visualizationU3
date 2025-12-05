# Pipeline ETL de Datos Meteorológicos en Tiempo Real

## 📋 Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Documentación Técnica del Código](#documentación-técnica-del-código)
7. [Base de Datos](#base-de-datos)
8. [Orquestación con Airflow](#orquestación-con-airflow)
9. [Uso y Comandos](#uso-y-comandos)
10. [Monitoreo y Debugging](#monitoreo-y-debugging)
11. [Troubleshooting](#troubleshooting)

---

## Descripción del Proyecto

Sistema completo de pipeline ELT (Extract, Load, Transform) para procesamiento de datos meteorológicos en tiempo real utilizando tecnologías modernas de ingeniería de datos. El proyecto recolecta datos climáticos de 10 ciudades globales, procesa la información a través de Apache Kafka, almacena los datos en PostgreSQL, orquesta flujos de trabajo con Apache Airflow y visualiza los resultados en un dashboard interactivo.

### Características Principales

- ✅ Recolección de datos meteorológicos en tiempo real de 10 ciudades
- ✅ Procesamiento de streaming con Apache Kafka
- ✅ Almacenamiento persistente en PostgreSQL
- ✅ Orquestación de workflows con Apache Airflow
- ✅ Transformaciones SQL para análisis de datos
- ✅ Dashboard de visualización interactivo
- ✅ Arquitectura completamente containerizada con Docker
- ✅ Monitoreo con Kafka UI y pgAdmin

---

## Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Apache Kafka** | 7.5.0 | Message broker para streaming de datos |
| **Apache Zookeeper** | 7.5.0 | Coordinación del cluster de Kafka |
| **PostgreSQL** | 15 | Base de datos relacional |
| **Apache Airflow** | Latest | Orquestación de workflows ETL |
| **Python** | 3.8+ | Lenguaje de programación principal |
| **Docker** | Latest | Containerización de servicios |
| **Kafka UI** | Latest | Interfaz web para monitoreo de Kafka |
| **pgAdmin** | Latest | Administración de PostgreSQL |

### Dependencias Python Principales

```
confluent-kafka==2.3.0      # Cliente de Kafka
psycopg2-binary==2.9.9      # Adaptador PostgreSQL
requests==2.31.0            # Cliente HTTP para API
python-dotenv==1.0.0        # Gestión de variables de entorno
apache-airflow==2.7.0       # Orquestación de workflows
```

---

## Arquitectura del Sistema

### Diagrama de Arquitectura

```
┌────────────────────────────────────────────────────────────────┐
│                      CAPA DE EXTRACCIÓN                        │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │  Open-Meteo API  │  ← Fuente externa de datos               │
│  │  (REST API)      │     meteorológicos                       │
│  └────────┬─────────┘                                          │
│           │ HTTP GET requests cada 18s                         │
│           ▼                                                     │
│  ┌──────────────────┐                                          │
│  │Weather Producer  │  ← Produce eventos a Kafka               │
│  │ (Python Script)  │    (producers/weather_producer.py)       │
│  └────────┬─────────┘                                          │
└───────────┼─────────────────────────────────────────────────────┘
            │
            │ JSON serializado
            ▼
┌────────────────────────────────────────────────────────────────┐
│                    CAPA DE STREAMING                           │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │            Apache Kafka Cluster                  │         │
│  │  ┌─────────────────────────────────────────┐    │         │
│  │  │  Topic: weather-events                  │    │         │
│  │  │  - Partitions: 1                        │    │         │
│  │  │  - Replication Factor: 1                │    │         │
│  │  │  - Retention: 7 days                    │    │         │
│  │  └─────────────────────────────────────────┘    │         │
│  │                                                   │         │
│  │  Coordinado por Zookeeper (puerto 2181)         │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │   Kafka UI       │  ← Monitoreo web del cluster            │
│  │  (puerto 8080)   │                                          │
│  └──────────────────┘                                          │
└───────────┬─────────────────────────────────────────────────────┘
            │
            │ Consume mensajes
            ▼
┌────────────────────────────────────────────────────────────────┐
│                      CAPA DE CARGA                             │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │Weather Consumer  │  ← Consume y escribe a BD                │
│  │ (Python Script)  │    (consumers/raw_to_postgres.py)        │
│  └────────┬─────────┘                                          │
│           │ INSERT statements                                  │
│           ▼                                                     │
│  ┌──────────────────────────────────────────────────┐         │
│  │          PostgreSQL Database                     │         │
│  │                                                   │         │
│  │  ┌────────────────────────────────┐              │         │
│  │  │  raw_weather_events            │              │         │
│  │  │  - Datos sin procesar          │              │         │
│  │  │  - JSONB con payload completo  │              │         │
│  │  │  - Índices en city y region    │              │         │
│  │  └────────────────────────────────┘              │         │
│  │                                                   │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │    pgAdmin       │  ← Administración web de BD              │
│  │  (puerto 5050)   │                                          │
│  └──────────────────┘                                          │
└───────────┬─────────────────────────────────────────────────────┘
            │
            │ SQL Transformations
            ▼
┌────────────────────────────────────────────────────────────────┐
│                  CAPA DE TRANSFORMACIÓN                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │           Apache Airflow                         │         │
│  │  ┌────────────────────────────────────────┐     │         │
│  │  │  DAG: weather_elt_pipeline             │     │         │
│  │  │  Schedule: @hourly                     │     │         │
│  │  │                                         │     │         │
│  │  │  Tasks:                                 │     │         │
│  │  │  1. produce_weather_to_kafka           │     │         │
│  │  │  2. consume_weather_to_postgres        │     │         │
│  │  │  3. transform_weather_data (SQL)       │     │         │
│  │  └────────────────────────────────────────┘     │         │
│  │                                                   │         │
│  │  - Webserver (puerto 8081)                      │         │
│  │  - Scheduler (background)                       │         │
│  └──────────────────────────────────────────────────┘         │
│           │                                                     │
│           │ Ejecuta SQL                                        │
│           ▼                                                     │
│  ┌──────────────────────────────────────────────────┐         │
│  │          PostgreSQL Database                     │         │
│  │                                                   │         │
│  │  ┌────────────────────────────────┐              │         │
│  │  │  analytics_weather             │              │         │
│  │  │  - Datos agregados por ciudad  │              │         │
│  │  │  - Métricas: avg, max, min     │              │         │
│  │  │  - Upsert por ciudad           │              │         │
│  │  └────────────────────────────────┘              │         │
│  │                                                   │         │
│  └──────────────────────────────────────────────────┘         │
└───────────┬─────────────────────────────────────────────────────┘
            │
            │ Query SELECT
            ▼
┌────────────────────────────────────────────────────────────────┐
│                   CAPA DE VISUALIZACIÓN                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │         Dashboard HTML                           │         │
│  │  - Gráficos interactivos                         │         │
│  │  - Métricas por ciudad                           │         │
│  │  - Visualización de tendencias                   │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Flujo de Datos Detallado

#### 1. Extracción (Extract)

**Componente**: `producers/weather_producer.py`

- Se ejecuta en loop infinito (o en modo batch para Airflow)
- Lee configuración de ciudades desde `data/cities.json`
- Para cada ciudad:
  - Hace request HTTP GET a Open-Meteo API
  - Construye un evento JSON con estructura definida
  - Publica el evento a Kafka con `city_id` como key
- Frecuencia: Cada 18 segundos para las 10 ciudades

**API Endpoint**: `https://api.open-meteo.com/v1/forecast`

**Parámetros consultados**:
- `temperature_2m`: Temperatura a 2 metros
- `relative_humidity_2m`: Humedad relativa
- `apparent_temperature`: Sensación térmica
- `is_day`: Indicador día/noche
- `precipitation`: Precipitación
- `weather_code`: Código de condición climática
- `cloud_cover`: Cobertura nubosa
- `wind_speed_10m`: Velocidad del viento

#### 2. Streaming (Message Broker)

**Componente**: Apache Kafka

- **Topic**: `weather-events`
- **Bootstrap Server**: `kafka:29092` (interno) / `localhost:9092` (externo)
- **Serialization**: JSON UTF-8
- **Key**: `city_id` (permite particionamiento por ciudad)
- **Auto-create topics**: Habilitado

**Zookeeper**: Gestiona el cluster de Kafka en puerto 2181

#### 3. Carga (Load)

**Componente**: `consumers/raw_to_postgres.py`

- Consumer group: `postgres-group`
- Auto-offset reset: `earliest` (lee desde el inicio si es nuevo consumer)
- Para cada mensaje:
  - Deserializa el JSON
  - Ejecuta INSERT en tabla `raw_weather_events`
  - Maneja conflictos con `ON CONFLICT DO NOTHING` (idempotencia)
  - Commit automático de offsets

#### 4. Transformación (Transform)

**Componente**: Airflow DAG + SQL Script

- **DAG**: `weather_elt_dag.py`
- **SQL**: `dags/sql/transform_weather.sql`
- **Operación**: Crea/actualiza tabla `analytics_weather`
- **Agregaciones**:
  - AVG(temperature_2m)
  - MAX(temperature_2m)
  - MIN(temperature_2m)
  - AVG(relative_humidity_2m)
  - SUM(precipitation_mm)
  - COUNT(*) de registros

**Upsert Strategy**: `ON CONFLICT (city) DO UPDATE` - actualiza estadísticas por ciudad

#### 5. Visualización

**Componente**: `dashboard/dashboard.html`

- Lee datos de tabla `analytics_weather`
- Genera gráficos y tablas interactivas
- Puede refrescarse para obtener últimos datos

### Comunicación entre Servicios

| Desde | Hacia | Protocolo | Puerto | Descripción |
|-------|-------|-----------|--------|-------------|
| Producer | Kafka | Kafka Protocol | 9092 | Publicación de eventos |
| Consumer | Kafka | Kafka Protocol | 9092 | Consumo de eventos |
| Consumer | PostgreSQL | PostgreSQL Wire | 5432 | Inserción de datos raw |
| Airflow | PostgreSQL | PostgreSQL Wire | 5432 | Transformaciones SQL |
| Airflow | Producer Script | Subprocess | - | Ejecución de Python |
| Airflow | Consumer Script | Subprocess | - | Ejecución de Python |
| Kafka | Zookeeper | Zookeeper Protocol | 2181 | Coordinación |
| Dashboard | PostgreSQL | PostgreSQL Wire | 5432 | Queries de lectura |

### Patrones de Diseño Implementados

1. **Producer-Consumer Pattern**: Desacoplamiento entre extracción y carga
2. **ELT over ETL**: Carga primero datos raw, transforma después
3. **Idempotency**: Consumer usa `ON CONFLICT DO NOTHING` para reintentos seguros
4. **Event Sourcing**: Almacena eventos completos en JSONB
5. **Batch + Stream Processing**: Soporta ambos modos de ejecución

---

## Instalación y Configuración

### Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **RAM** | 4 GB | 8 GB+ |
| **CPU** | 2 cores | 4 cores+ |
| **Disco** | 5 GB libres | 10 GB+ |
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04 | Últimas versiones |

### Software Prerequisito

#### 1. Docker y Docker Compose

**Linux (Ubuntu/Debian)**:
```bash
# Actualizar paquetes
sudo apt-get update

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt-get install docker-compose-plugin

# Verificar instalación
docker --version
docker compose version
```

**macOS**:
```bash
# Instalar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop

# Verificar
docker --version
docker compose version
```

**Windows**:
```powershell
# Instalar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop

# Verificar en PowerShell
docker --version
docker compose version
```

#### 2. Python 3.8+

**Linux**:
```bash
sudo apt-get install python3 python3-pip python3-venv
python3 --version
```

**macOS**:
```bash
brew install python@3.11
python3 --version
```

**Windows**:
- Descargar desde https://www.python.org/downloads/
- Marcar "Add Python to PATH" durante instalación
- Verificar en CMD: `python --version`

#### 3. Git

**Linux**:
```bash
sudo apt-get install git
git --version
```

**macOS**:
```bash
brew install git
git --version
```

**Windows**:
- Descargar desde https://git-scm.com/download/win
- Verificar: `git --version`

### Pasos de Instalación

#### Paso 1: Clonar el Repositorio

```bash
# Clonar el proyecto
git clone https://github.com/damapech1/visualizationU3.git

# Navegar al directorio
cd visualizationU3

# Verificar contenido
ls -la
```

Deberías ver:
```
docker-compose.yml
Dockerfile.airflow
init.sql
requirements.txt
dags/
producers/
consumers/
dashboard/
data/
```

#### Paso 2: Configurar Variables de Entorno

El archivo `.env` ya está configurado con valores por defecto:

```bash
# Ver configuración actual
cat .env
```

Contenido del `.env`:
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=weather-events

POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=weather_db
POSTGRES_USER=kafka_user
POSTGRES_PASSWORD=kafka123
```

**Nota**: Para producción, cambiar las credenciales de PostgreSQL.

#### Paso 3: Iniciar Servicios con Docker Compose

```bash
# Iniciar todos los servicios en segundo plano
docker-compose up -d

# Esto iniciará:
# - zookeeper (coordinación de Kafka)
# - kafka (message broker)
# - kafka-ui (interfaz web)
# - postgres (base de datos)
# - pgadmin (admin de BD)
# - airflow-webserver (UI de Airflow)
# - airflow-scheduler (programador de tareas)
```

**Tiempo estimado**: 2-3 minutos para que todos los servicios estén listos.

#### Paso 4: Verificar Estado de Servicios

```bash
# Ver estado de todos los contenedores
docker-compose ps
```

**Output esperado**:
```
NAME                  STATUS
airflow-scheduler     Up (healthy)
airflow-webserver     Up (healthy)
kafka                 Up
kafka-ui              Up
pgadmin               Up
postgres              Up (healthy)
zookeeper             Up
```

#### Paso 5: Verificar Conectividad

```bash
# Test 1: Verificar PostgreSQL
docker exec -it postgres pg_isready -U kafka_user
# Salida esperada: accepting connections

# Test 2: Ver tablas en PostgreSQL
docker exec -it postgres psql -U kafka_user -d weather_db -c "\dt"
# Debería mostrar: raw_weather_events

# Test 3: Verificar Kafka UI
curl -I http://localhost:8080
# Debería retornar: HTTP/1.1 200 OK

# Test 4: Verificar Airflow
curl -I http://localhost:8081/health
# Debería retornar: HTTP/1.1 200 OK
```

#### Paso 6: Configurar Entorno Python (Opcional para desarrollo)

Si quieres ejecutar scripts manualmente fuera de Docker:

```bash
# Crear entorno virtual
python3 -m venv kafka-etl-env

# Activar entorno
# En Linux/macOS:
source kafka-etl-env/bin/activate

# En Windows:
kafka-etl-env\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep confluent-kafka
```

#### Paso 7: Acceder a Interfaces Web

Abrir en el navegador:

1. **Kafka UI**: http://localhost:8080
   - Ver topics, mensajes, consumer groups
   - No requiere login

2. **Airflow**: http://localhost:8081
   - Usuario: `airflow`
   - Contraseña: `airflow`
   - Activar el DAG `weather_elt_pipeline`

3. **pgAdmin**: http://localhost:5050
   - Email: `admin@admin.com`
   - Contraseña: `admin`
   - Conectar a servidor PostgreSQL:
     - Host: `postgres`
     - Port: `5432`
     - Database: `weather_db`
     - User: `kafka_user`
     - Password: `kafka123`

#### Paso 8: Ejecutar Pipeline Manualmente (Primera Vez)

Opción A - Desde Airflow (Recomendado):
1. Ir a http://localhost:8081
2. Login con `airflow` / `airflow`
3. Buscar DAG `weather_elt_pipeline`
4. Click en el toggle para activarlo
5. Click en "Trigger DAG" (botón de play)
6. Monitorear ejecución en la vista de Graph

Opción B - Desde línea de comandos:
```bash
# Terminal 1: Iniciar Producer
docker exec -it airflow-webserver python /opt/airflow/producers/weather_producer.py --batch

# Terminal 2: Iniciar Consumer
docker exec -it airflow-webserver python /opt/airflow/consumers/raw_to_postgres.py --batch

# Terminal 3: Verificar datos
docker exec -it postgres psql -U kafka_user -d weather_db -c "SELECT city, temperature_2m, captured_at FROM raw_weather_events ORDER BY captured_at DESC LIMIT 10;"
```

#### Paso 9: Verificar Dashboard

```bash
# Abrir dashboard en navegador
# Opción 1: Abrir archivo directamente
open dashboard/dashboard.html

# Opción 2: Servir con Python
cd dashboard
python -m http.server 8000
# Luego abrir: http://localhost:8000/dashboard.html
```

### Configuración Avanzada

#### Cambiar Frecuencia de Producer

Editar `producers/weather_producer.py` línea 74:
```python
time.sleep(18)  # Cambiar a segundos deseados
```

#### Agregar Más Ciudades

Editar `data/cities.json`:
```json
{
  "city_id": 11,
  "name": "Nueva Ciudad",
  "latitude": 0.0,
  "longitude": 0.0,
  "region": "Region",
  "segment": "segment"
}
```

#### Cambiar Schedule de Airflow DAG

Editar `dags/weather_elt_dag.py` línea 19:
```python
schedule_interval='@hourly',  # Cambiar a: '@daily', '@weekly', etc.
```

### Troubleshooting de Instalación

#### Error: Puerto ya en uso

```bash
# Ver qué proceso usa el puerto
# Linux/macOS:
lsof -i :8080

# Windows:
netstat -ano | findstr :8080

# Cambiar puerto en docker-compose.yml
# Por ejemplo, cambiar 8080:8080 a 8081:8080
```

#### Error: No hay espacio en disco

```bash
# Limpiar imágenes y contenedores no usados
docker system prune -a

# Ver uso de espacio
docker system df
```

#### Error: Servicios no inician (recursos insuficientes)

```bash
# Aumentar recursos en Docker Desktop:
# Settings > Resources > Memory: 4GB+

# O iniciar solo servicios esenciales
docker-compose up -d zookeeper kafka postgres
```

#### Error: Airflow no puede conectar a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Reiniciar Airflow
docker-compose restart airflow-webserver airflow-scheduler

# Ver logs
docker-compose logs airflow-webserver
```

---

## Estructura del Proyecto

```
visualizationU3/
│
├── 📁 dags/                              # Airflow DAGs y workflows
│   ├── weather_elt_dag.py                # DAG principal del pipeline ETL
│   ├── __pycache__/                      # Caché de Python
│   └── 📁 sql/                           # Scripts SQL de transformación
│       └── transform_weather.sql         # Agregaciones y métricas
│
├── 📁 producers/                         # Productores de Kafka
│   └── weather_producer.py               # Extrae datos de Open-Meteo API
│                                          # Publica eventos a topic Kafka
│
├── 📁 consumers/                         # Consumidores de Kafka
│   └── raw_to_postgres.py                # Lee de Kafka y escribe a PostgreSQL
│                                          # Maneja inserción de datos raw
│
├── 📁 dashboard/                         # Capa de visualización
│   └── dashboard.html                    # Dashboard interactivo con gráficos
│                                          # Conecta a analytics_weather
│
├── 📁 data/                              # Datos estáticos y configuración
│   ├── cities.json                       # Lista de 10 ciudades a monitorear
│   │                                     # Incluye: coordenadas, región, segmento
│   └── weather_data.json                 # Datos de ejemplo/cache
│
├── 📁 logs/                              # Logs de Airflow
│   ├── dag_id=weather_elt_pipeline/      # Logs por DAG
│   └── scheduler/                        # Logs del scheduler
│
├── 📁 plugins/                           # Plugins custom de Airflow (vacío)
│
├── 📄 docker-compose.yml                 # Orquestación de 7 servicios Docker:
│                                          # - zookeeper, kafka, kafka-ui
│                                          # - postgres, pgadmin
│                                          # - airflow-webserver, airflow-scheduler
│
├── 📄 Dockerfile.airflow                 # Imagen custom de Airflow
│                                          # Instala dependencias Python
│
├── 📄 init.sql                           # Script de inicialización de PostgreSQL
│                                          # Crea tabla raw_weather_events
│                                          # Define índices
│
├── 📄 requirements.txt                   # Dependencias Python del proyecto:
│                                          # confluent-kafka, psycopg2, requests
│
├── 📄 requirements_airflow.txt           # Dependencias específicas de Airflow
│
├── 📄 .env                               # Variables de entorno:
│                                          # Kafka, PostgreSQL configs
│
├── 📄 .git/                              # Control de versiones Git
│
├── 📄 README.md                          # Este archivo (documentación completa)
│
└── 📄 CLAUDE.MD                          # Documentación para Claude AI
```

### Descripción Detallada de Componentes

#### `/dags/`

Contiene las definiciones de workflows de Airflow (DAGs - Directed Acyclic Graphs).

**weather_elt_dag.py** (45 líneas):
- Define el DAG `weather_elt_pipeline`
- Schedule: Ejecución cada hora (`@hourly`)
- 3 tareas secuenciales:
  1. `produce_weather_to_kafka`: BashOperator que ejecuta producer
  2. `consume_weather_to_postgres`: BashOperator que ejecuta consumer
  3. `transform_weather_data`: PostgresOperator que ejecuta SQL
- Dependencias: `produce >> consume >> transform`

**sql/transform_weather.sql** (40 líneas):
- Crea tabla `analytics_weather` si no existe
- Ejecuta agregaciones: AVG, MAX, MIN, SUM, COUNT
- Implementa UPSERT con `ON CONFLICT DO UPDATE`
- Agrupa por ciudad

#### `/producers/`

Scripts que extraen datos de fuentes externas y publican a Kafka.

**weather_producer.py** (74 líneas):
- Lee configuración de `data/cities.json`
- Loop infinito (o batch mode con flag `--batch`)
- Para cada ciudad:
  - GET request a Open-Meteo API
  - Construye evento con UUID único
  - Publica a topic `weather-events` con `city_id` como key
- Manejo de errores: skip ciudad si falla API
- Callback de delivery para confirmar publicación
- Frecuencia: 18 segundos entre iteraciones

#### `/consumers/`

Scripts que consumen mensajes de Kafka y los procesan.

**raw_to_postgres.py** (71 líneas):
- Consumer de Kafka con group ID `postgres-group`
- Auto-offset reset: `earliest` (procesa histórico)
- Conexión persistente a PostgreSQL
- Para cada mensaje:
  - Deserializa JSON
  - INSERT en `raw_weather_events`
  - ON CONFLICT DO NOTHING (idempotencia)
  - Commit de transacción
- Soporta batch mode con timeout de 30 segundos
- Manejo de errores con rollback

#### `/dashboard/`

Interfaz web para visualización de datos.

**dashboard.html** (estimado ~500 líneas):
- Frontend HTML/CSS/JavaScript
- Gráficos con Chart.js o similar
- Consulta tabla `analytics_weather`
- Muestra métricas por ciudad:
  - Temperaturas: promedio, máxima, mínima
  - Humedad promedio
  - Precipitación total
  - Conteo de registros

#### `/data/`

Datos estáticos y configuración.

**cities.json** (12 líneas):
- Array de 10 ciudades
- Campos: city_id, name, latitude, longitude, region, segment
- Regiones: Latam (7), Europa (2), Norte (1)
- Segmentos: urban, premium, coastal, altitude

**weather_data.json**:
- Datos de ejemplo o cache
- Formato igual a eventos de Kafka

#### Archivos de Configuración

**docker-compose.yml** (133 líneas):
- Define 7 servicios
- Networking interno con DNS automático
- Volúmenes para persistencia
- Variables de entorno para cada servicio
- Health checks para servicios críticos
- Mapeo de puertos a host

**Dockerfile.airflow**:
```dockerfile
FROM apache/airflow:2.7.0
COPY requirements_airflow.txt .
RUN pip install -r requirements_airflow.txt
```

**init.sql** (26 líneas):
- DROP TABLE IF EXISTS
- CREATE TABLE con 17 columnas
- Tipos: SERIAL, VARCHAR, INT, FLOAT, BOOLEAN, JSONB, TIMESTAMP
- UNIQUE constraint en event_id
- 2 índices: idx_city, idx_region

**.env** (8 líneas):
- Configuración de Kafka (bootstrap servers, topic)
- Configuración de PostgreSQL (host, port, database, credentials)

---

## Documentación Técnica del Código

### Producer: `weather_producer.py`

#### Descripción General

Script Python que actúa como productor de Kafka, extrayendo datos meteorológicos de la API de Open-Meteo y publicándolos en un topic de Kafka para su posterior procesamiento.

#### Dependencias

```python
import json          # Serialización de datos
import time          # Control de frecuencia de polling
import requests      # Cliente HTTP para API externa
import uuid          # Generación de IDs únicos
import sys           # Argumentos de línea de comandos
from datetime import datetime           # Timestamps
from confluent_kafka import Producer    # Cliente de Kafka
from dotenv import load_dotenv          # Variables de entorno
import os            # Acceso a variables de entorno
```

#### Configuración

```python
load_dotenv()  # Carga variables desde .env

TOPIC = os.getenv("KAFKA_TOPIC")                      # "weather-events"
BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")      # "localhost:9092"

# Resolución de ruta relativa para cities.json
current_dir = os.path.dirname(os.path.abspath(__file__))
cities_path = os.path.join(current_dir, '../data/cities.json')

with open(cities_path) as f:
    cities = json.load(f)  # Lista de 10 ciudades
```

#### Inicialización del Producer

```python
p = Producer({'bootstrap.servers': BOOTSTRAP})
```

**Configuración mínima**:
- `bootstrap.servers`: Dirección del broker de Kafka
- Sin configuración de serialización (usa bytes nativos)
- Sin compresión
- Sin configuración de batch (usa defaults)

#### Función: `delivery_report()`

```python
def delivery_report(err, msg):
    """
    Callback invocado al confirmar entrega del mensaje.

    Args:
        err: Error object si falla, None si éxito
        msg: Metadata del mensaje enviado

    Comportamiento:
        - Solo imprime si hay error
        - No maneja retry logic (eso lo hace Kafka client)
    """
    if err:
        print(f"Error: {err}")
```

**Uso**: Se pasa como callback a `producer.produce()`

#### Función: `get_weather(lat, lon)`

```python
def get_weather(lat, lon):
    """
    Consulta API de Open-Meteo para obtener datos meteorológicos actuales.

    Args:
        lat (float): Latitud de la ubicación
        lon (float): Longitud de la ubicación

    Returns:
        dict: Objeto "current" del JSON de respuesta, o None si falla

    API:
        - Endpoint: https://api.open-meteo.com/v1/forecast
        - Método: GET
        - Timeout: 8 segundos
        - Rate limit: Sin límite para uso no comercial

    Parámetros consultados:
        - temperature_2m: Temperatura a 2 metros (°C)
        - relative_humidity_2m: Humedad relativa (%)
        - apparent_temperature: Sensación térmica (°C)
        - is_day: 1 si es de día, 0 si es de noche
        - precipitation: Precipitación (mm)
        - weather_code: Código WMO de condición climática
        - cloud_cover: Cobertura nubosa (%)
        - wind_speed_10m: Velocidad del viento a 10m (km/h)
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,wind_speed_10m"
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()  # Lanza excepción si status code != 200
        return r.json()["current"]
    except:
        # Captura cualquier error: timeout, network, JSON parse, etc.
        return None
```

**Estructura de respuesta de la API**:
```json
{
  "current": {
    "time": "2025-12-05T10:00",
    "temperature_2m": 22.5,
    "relative_humidity_2m": 65,
    "apparent_temperature": 23.1,
    "is_day": 1,
    "precipitation": 0.0,
    "weather_code": 3,
    "cloud_cover": 75,
    "wind_speed_10m": 12.3
  }
}
```

#### Loop Principal

```python
print("Weather Producer iniciado – Open-Meteo API")

while True:
    for city in cities:
        # 1. Obtener datos meteorológicos
        data = get_weather(city["latitude"], city["longitude"])
        if not data:
            continue  # Skip ciudad si falla API

        # 2. Construir evento
        event = {
            # Identificadores únicos
            "event_id": str(uuid.uuid4()),              # UUID v4 único por evento
            "city_id": city["city_id"],                 # ID de ciudad (1-10)

            # Información geográfica
            "city": city["name"],                       # Nombre de ciudad
            "region": city["region"],                   # Latam, Europa, Norte
            "segment": city["segment"],                 # urban, premium, coastal, altitude
            "latitude": city["latitude"],               # Coordenada
            "longitude": city["longitude"],             # Coordenada

            # Datos meteorológicos (del API)
            "timestamp": data["time"],                  # ISO 8601 desde API
            "temperature_2m": data.get("temperature_2m"),
            "relative_humidity_2m": data.get("relative_humidity_2m"),
            "apparent_temperature": data.get("apparent_temperature"),
            "is_day": bool(data.get("is_day")),         # Convierte 0/1 a boolean
            "precipitation_mm": data.get("precipitation"),
            "weather_code": data.get("weather_code"),
            "cloud_cover": data.get("cloud_cover"),
            "wind_speed_kmh": data.get("wind_speed_10m"),

            # Metadata de captura
            "captured_at": datetime.utcnow().isoformat()  # Timestamp de procesamiento
        }

        # 3. Publicar a Kafka
        p.produce(
            TOPIC,                              # Topic: "weather-events"
            key=str(city["city_id"]),           # Key para particionamiento
            value=json.dumps(event).encode(),   # Serializa a JSON bytes
            callback=delivery_report            # Callback de confirmación
        )

        # 4. Log de progreso
        print(f"{city['name']}: {event['temperature_2m']}°C")

    # 5. Flush para asegurar envío
    p.flush()  # Bloquea hasta que todos los mensajes sean enviados

    # 6. Check batch mode
    if "--batch" in sys.argv:
        print("Batch mode: Finalizando después de una iteración.")
        break

    # 7. Esperar antes de siguiente iteración
    time.sleep(18)  # 18 segundos * 10 ciudades = ~3 minutos por ciclo completo
```

#### Características Clave

**1. Idempotencia**:
- Cada evento tiene `event_id` único (UUID v4)
- Consumer puede usar `ON CONFLICT DO NOTHING`

**2. Particionamiento**:
- Key = `city_id` permite:
  - Mantener orden de eventos por ciudad
  - Distribuir carga si hay múltiples particiones
  - Facilitar procesamiento por ciudad

**3. Manejo de Errores**:
- API failures: Skip ciudad, continúa con siguientes
- Kafka failures: Callback imprime error, no detiene proceso
- Network timeouts: 8 segundos por request

**4. Batch Mode**:
- Flag `--batch` para uso en Airflow
- Ejecuta una sola iteración y termina
- Útil para programación horaria

**5. Metadata Rica**:
- `timestamp`: Tiempo según API (momento de medición)
- `captured_at`: Tiempo de procesamiento del producer
- Diferencia permite medir latencia de pipeline

#### Performance

- **Throughput**: 10 ciudades cada 18 segundos = ~33 eventos/minuto
- **Latency**: ~8 segundos max por ciudad (API timeout)
- **Network**: ~1 KB por evento
- **API Calls**: 10 calls cada 18 segundos = ~2400 calls/hora

---

### Consumer: `raw_to_postgres.py`

#### Descripción General

Script Python que consume eventos de Kafka y los persiste en PostgreSQL, actuando como la capa de carga (Load) del pipeline ETL.

#### Dependencias

```python
import os                               # Variables de entorno
import json                             # Deserialización de eventos
import psycopg2                         # Adaptador de PostgreSQL
import sys                              # Argumentos CLI
import time                             # Para batch mode timing
from confluent_kafka import Consumer    # Cliente Kafka
from dotenv import load_dotenv          # Cargar .env
```

#### Configuración del Consumer

```python
load_dotenv()

# Inicializar Kafka Consumer
c = Consumer({
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),  # "localhost:9092"
    'group.id': 'postgres-group',          # Consumer group para coordinar offsets
    'auto.offset.reset': 'earliest'        # Lee desde inicio si no hay offset guardado
})

c.subscribe([os.getenv('KAFKA_TOPIC')])    # Subscribe a "weather-events"
```

**Configuración del Consumer Group**:
- `group.id`: Identifica este consumer group
- Kafka mantiene offset por grupo
- Múltiples consumers con mismo group.id comparten carga
- `auto.offset.reset`: `earliest` procesa histórico, `latest` solo nuevos

#### Configuración de PostgreSQL

```python
# Conexión persistente a PostgreSQL
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),          # "localhost" o "postgres" en Docker
    port=os.getenv('POSTGRES_PORT'),          # "5432"
    dbname=os.getenv('POSTGRES_DB'),          # "weather_db"
    user=os.getenv('POSTGRES_USER'),          # "kafka_user"
    password=os.getenv('POSTGRES_PASSWORD')   # "kafka123"
)

cur = conn.cursor()  # Cursor para ejecutar queries
```

**Características de la conexión**:
- Conexión persistente (no se cierra en cada mensaje)
- Autocommit deshabilitado (control manual de transacciones)
- Cursor reutilizable

#### Configuración de Batch Mode

```python
print("Consumer → PostgreSQL iniciado")

batch_mode = "--batch" in sys.argv       # Detecta flag --batch
no_message_count = 0                     # Contador de polling sin mensajes
max_no_message_retries = 30              # Timeout: 30 segundos sin mensajes
```

#### Loop Principal de Consumo

```python
while True:
    # 1. Poll de Kafka (espera hasta 1 segundo por mensaje)
    msg = c.poll(1.0)

    # 2. Manejo de ausencia de mensajes
    if msg is None:
        if batch_mode:
            no_message_count += 1
            print(f"Batch mode: Esperando mensajes... ({no_message_count}/{max_no_message_retries})")

            if no_message_count >= max_no_message_retries:
                print("Batch mode: Timeout alcanzado sin nuevos mensajes. Finalizando.")
                break
        continue  # Siguiente iteración

    # 3. Reset contador si recibimos mensaje
    if batch_mode:
        no_message_count = 0

    # 4. Manejo de errores de Kafka
    if msg.error():
        print(msg.error())
        continue

    # 5. Deserializar mensaje
    data = json.loads(msg.value())

    # 6. Insertar en PostgreSQL
    try:
        cur.execute("""
            INSERT INTO raw_weather_events (
                event_id, city_id, city, region, segment,
                latitude, longitude,
                temperature_2m, relative_humidity_2m, apparent_temperature,
                is_day, precipitation_mm, weather_code, cloud_cover,
                wind_speed_kmh, raw_json
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (event_id) DO NOTHING
        """, (
            data['event_id'],
            data['city_id'],
            data['city'],
            data['region'],
            data['segment'],
            data['latitude'],
            data['longitude'],
            data['temperature_2m'],
            data['relative_humidity_2m'],
            data['apparent_temperature'],
            data['is_day'],
            data['precipitation_mm'],
            data['weather_code'],
            data['cloud_cover'],
            data['wind_speed_kmh'],
            json.dumps(data)  # Almacena JSON completo en columna JSONB
        ))

        conn.commit()  # Commit de transacción

        print(f"Insertado → {data['city']} {data['temperature_2m']}°C")

    except Exception as e:
        print(f"Error insertando en BD: {e}")
        conn.rollback()  # Rollback en caso de error
```

#### Características Clave

**1. Idempotencia**:
```sql
ON CONFLICT (event_id) DO NOTHING
```
- Permite reintentos seguros
- Evita duplicados si consumer reprocesa mensajes
- Útil si consumer falla y relee offsets

**2. Gestión de Transacciones**:
```python
conn.commit()    # Éxito
conn.rollback()  # Error
```
- Control manual de transacciones
- Rollback previene datos inconsistentes
- Un error no afecta mensajes previos

**3. Almacenamiento del JSON Completo**:
```python
raw_json = json.dumps(data)  # Columna JSONB
```
- Preserva evento original
- Permite futuras transformaciones sin reprocesar Kafka
- Facilita debugging y auditoría

**4. Batch Mode**:
- Útil para Airflow DAG
- Espera hasta 30 segundos por nuevos mensajes
- Termina automáticamente cuando no hay más datos

**5. Offset Management**:
- Kafka automáticamente guarda offsets por consumer group
- Si consumer se detiene y reinicia, continúa desde último offset
- No pierde ni reprocesa mensajes (exactly-once semántico con idempotencia)

#### Patrones de Diseño

**1. At-Least-Once Delivery + Idempotence = Exactly-Once Semántico**:
```
Kafka garantiza at-least-once
+
ON CONFLICT DO NOTHING
=
Exactly-once en BD
```

**2. Connection Pooling Simplificado**:
- Una conexión persistente
- Reutiliza cursor
- Más eficiente que abrir/cerrar por mensaje

**3. Error Handling Granular**:
```python
try:
    # INSERT
    conn.commit()
except:
    conn.rollback()  # Solo afecta transacción actual
    # Consumer continúa con siguiente mensaje
```

#### Performance

- **Latency**: ~1ms por INSERT (local)
- **Throughput**: Limitado por velocidad de producer (~33 msg/min)
- **Batch Size**: Procesa 1 mensaje a la vez (puede optimizarse)
- **Memory**: Mínima (no guarda mensajes en memoria)

---

### Airflow DAG: `weather_elt_dag.py`

#### Descripción General

Define el workflow de orquestación que ejecuta el pipeline completo de ELT (Extract, Load, Transform) de manera programada.

#### Dependencias

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta
```

#### Configuración del DAG

```python
default_args = {
    'owner': 'airflow',              # Propietario del DAG
    'depends_on_past': False,        # No depende de ejecuciones previas
    'email_on_failure': False,       # No envía email en fallos
    'email_on_retry': False,         # No envía email en reintentos
    'retries': 1,                    # Reintenta una vez si falla
    'retry_delay': timedelta(minutes=5),  # Espera 5 min antes de reintentar
}
```

#### Definición del DAG

```python
with DAG(
    'weather_elt_pipeline',                    # Nombre único del DAG
    default_args=default_args,
    description='A simple ELT pipeline for weather data using Kafka and Postgres',
    schedule_interval='@hourly',               # Ejecuta cada hora
    start_date=datetime(2023, 1, 1),          # Fecha de inicio
    catchup=False,                             # No ejecuta fechas pasadas
    tags=['weather', 'elt', 'kafka'],         # Tags para organización
) as dag:
```

**Schedule Intervals comunes**:
- `@hourly`: Cada hora
- `@daily`: Cada día a medianoche
- `@weekly`: Cada semana
- `'*/15 * * * *'`: Cada 15 minutos (cron syntax)

#### Task 1: Produce Weather Data

```python
produce_weather = BashOperator(
    task_id='produce_weather_to_kafka',
    bash_command='python /opt/airflow/producers/weather_producer.py --batch',
)
```

**Comportamiento**:
- Ejecuta producer en modo batch
- Recoge datos de 10 ciudades
- Publica a Kafka
- Termina después de una iteración
- Si falla (exit code != 0), Airflow lo detecta

#### Task 2: Consume Weather Data

```python
consume_weather = BashOperator(
    task_id='consume_weather_to_postgres',
    bash_command='python /opt/airflow/consumers/raw_to_postgres.py --batch',
)
```

**Comportamiento**:
- Consume mensajes de Kafka
- Escribe a PostgreSQL
- Espera hasta 30 segundos por nuevos mensajes
- Termina cuando no hay más datos
- Maneja errores con retry logic

#### Task 3: Transform Weather Data

```python
transform_weather = PostgresOperator(
    task_id='transform_weather_data',
    postgres_conn_id='postgres_default',      # Usa conexión configurada en Airflow
    sql='sql/transform_weather.sql',          # Path relativo a /opt/airflow/dags
)
```

**Comportamiento**:
- Ejecuta SQL script de transformación
- Crea/actualiza tabla `analytics_weather`
- Hace agregaciones: AVG, MAX, MIN, SUM, COUNT
- Implementa UPSERT por ciudad

#### Definición de Dependencias

```python
produce_weather >> consume_weather >> transform_weather
```

**Flujo**:
```
produce_weather (extrae y publica)
    ↓
consume_weather (lee y carga)
    ↓
transform_weather (agrega y transforma)
```

**Comportamiento ante fallos**:
- Si `produce_weather` falla → No ejecuta tasks siguientes
- Si `consume_weather` falla → No ejecuta `transform_weather`
- Cada task reintenta 1 vez con 5 min de delay

#### Airflow Connection Setup

Para que `PostgresOperator` funcione, necesita una conexión configurada:

**Método 1 - Variable de Entorno** (Ya configurado en docker-compose.yml):
```yaml
AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://kafka_user:kafka123@postgres:5432/weather_db
```

**Método 2 - Airflow UI**:
1. Admin → Connections → Add
2. Connection Id: `postgres_default`
3. Connection Type: `Postgres`
4. Host: `postgres`
5. Schema: `weather_db`
6. Login: `kafka_user`
7. Password: `kafka123`
8. Port: `5432`

#### Monitoreo del DAG

**En Airflow UI** (http://localhost:8081):

1. **DAGs View**: Lista todos los DAGs
   - Toggle para activar/desactivar
   - Botón "Trigger DAG" para ejecución manual

2. **Graph View**: Visualización de tasks y dependencias
   - Verde: Éxito
   - Rojo: Fallo
   - Amarillo: En ejecución
   - Blanco: No ejecutado

3. **Logs**: Click en task → View Log
   - Ver stdout/stderr de cada task
   - Útil para debugging

4. **Gantt Chart**: Timeline de ejecuciones
   - Ver duración de cada task
   - Identificar cuellos de botella

#### Características Avanzadas

**1. Templating con Jinja2**:
```python
bash_command='python script.py --date {{ ds }}'  # ds = execution date
```

**2. XComs para compartir datos entre tasks**:
```python
# Task 1
ti.xcom_push(key='my_key', value=data)

# Task 2
data = ti.xcom_pull(task_ids='task1', key='my_key')
```

**3. Branch Operators para lógica condicional**:
```python
from airflow.operators.python import BranchPythonOperator
```

**4. Sensors para esperar condiciones**:
```python
from airflow.sensors.filesystem import FileSensor
```

---

### SQL Transformations: `transform_weather.sql`

#### Descripción General

Script SQL que crea la tabla de analytics y ejecuta transformaciones de agregación sobre los datos raw.

#### Parte 1: Crear Tabla Analytics

```sql
-- Create analytics table if it doesn't exist
CREATE TABLE IF NOT EXISTS analytics_weather (
    analytics_id SERIAL PRIMARY KEY,           -- Auto-incrementing ID
    city VARCHAR(100) UNIQUE,                  -- Nombre de ciudad (clave de negocio)
    avg_temperature FLOAT,                     -- Temperatura promedio
    max_temperature FLOAT,                     -- Temperatura máxima registrada
    min_temperature FLOAT,                     -- Temperatura mínima registrada
    avg_humidity FLOAT,                        -- Humedad promedio
    total_precipitation FLOAT,                 -- Precipitación acumulada
    record_count INT,                          -- Número de registros procesados
    last_updated TIMESTAMP DEFAULT NOW()       -- Timestamp de última actualización
);
```

**Características**:
- **SERIAL**: Auto-incrementa para cada fila
- **UNIQUE constraint en city**: Permite UPSERT
- **FLOAT**: Tipo de dato para valores decimales
- **INT**: Contador de registros
- **TIMESTAMP**: Auditoría de actualizaciones

#### Parte 2: Transform y Load (UPSERT)

```sql
INSERT INTO analytics_weather (
    city,
    avg_temperature,
    max_temperature,
    min_temperature,
    avg_humidity,
    total_precipitation,
    record_count,
    last_updated
)
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
```

#### Desglose de la Query

**1. Agregaciones**:
```sql
AVG(temperature_2m)         -- Promedio de todas las mediciones
MAX(temperature_2m)         -- Temperatura más alta registrada
MIN(temperature_2m)         -- Temperatura más baja registrada
AVG(relative_humidity_2m)   -- Humedad promedio
SUM(precipitation_mm)       -- Precipitación total acumulada
COUNT(*)                    -- Número de mediciones
```

**2. GROUP BY**:
```sql
GROUP BY city  -- Una fila por ciudad en el resultado
```

**3. UPSERT (ON CONFLICT)**:
```sql
ON CONFLICT (city)           -- Si ciudad ya existe
DO UPDATE SET                -- Actualiza valores existentes
    avg_temperature = EXCLUDED.avg_temperature,  -- EXCLUDED = nuevos valores
    ...
    last_updated = NOW()     -- Actualiza timestamp
```

**Ventajas del UPSERT**:
- No necesita verificar si ciudad existe
- Atómico (no hay race conditions)
- Mantiene analytics_id original
- Actualiza solo lo necesario

#### Ejemplo de Transformación

**Datos Raw** (tabla `raw_weather_events`):
```
| event_id | city           | temperature_2m | humidity | precipitation |
|----------|----------------|----------------|----------|---------------|
| uuid1    | Ciudad de México | 22.5         | 65       | 0.0          |
| uuid2    | Ciudad de México | 23.1         | 62       | 0.0          |
| uuid3    | Ciudad de México | 21.8         | 68       | 0.5          |
```

**Resultado Agregado** (tabla `analytics_weather`):
```
| city             | avg_temp | max_temp | min_temp | avg_humidity | total_precip | count |
|------------------|----------|----------|----------|--------------|--------------|-------|
| Ciudad de México | 22.47    | 23.1     | 21.8     | 65.0         | 0.5          | 3     |
```

#### Consideraciones de Performance

**1. Índices**:
```sql
-- Ya creados en init.sql
CREATE INDEX idx_city ON raw_weather_events(city);
CREATE INDEX idx_region ON raw_weather_events(region);
```

**2. Query Optimization**:
- `GROUP BY city` usa índice `idx_city`
- Agregaciones se calculan en una sola pasada
- UPSERT es más rápido que DELETE + INSERT

**3. Escalabilidad**:
- Para millones de registros, considerar:
  - Particionamiento por fecha
  - Agregaciones incrementales
  - Materializar vistas (MATERIALIZED VIEW)

#### Alternativas de Transformación

**1. Agregación por Día**:
```sql
SELECT
    city,
    DATE(captured_at) as date,
    AVG(temperature_2m) as daily_avg_temp
FROM raw_weather_events
GROUP BY city, DATE(captured_at)
```

**2. Agregación por Región**:
```sql
SELECT
    region,
    AVG(temperature_2m) as avg_temperature,
    COUNT(DISTINCT city) as city_count
FROM raw_weather_events
GROUP BY region
```

**3. Time-Series Analysis**:
```sql
SELECT
    city,
    DATE_TRUNC('hour', captured_at) as hour,
    AVG(temperature_2m) as hourly_avg
FROM raw_weather_events
GROUP BY city, DATE_TRUNC('hour', captured_at)
ORDER BY city, hour
```

---

### Database Schema: `init.sql`

#### Tabla: raw_weather_events

```sql
DROP TABLE IF EXISTS raw_weather_events;

CREATE TABLE raw_weather_events (
    -- Identificadores
    id SERIAL PRIMARY KEY,                    -- ID auto-incremental (surrogate key)
    event_id VARCHAR(50) UNIQUE,              -- UUID del evento (natural key, único)
    city_id INT,                              -- ID de ciudad (1-10)

    -- Información geográfica
    city VARCHAR(100),                        -- Nombre de ciudad
    region VARCHAR(50),                       -- Latam, Europa, Norte
    segment VARCHAR(50),                      -- urban, premium, coastal, altitude
    latitude FLOAT,                           -- Coordenada geográfica
    longitude FLOAT,                          -- Coordenada geográfica

    -- Datos meteorológicos
    temperature_2m FLOAT,                     -- Temperatura a 2m (°C)
    relative_humidity_2m FLOAT,               -- Humedad relativa (%)
    apparent_temperature FLOAT,               -- Sensación térmica (°C)
    is_day BOOLEAN,                           -- true=día, false=noche
    precipitation_mm FLOAT,                   -- Precipitación (mm)
    weather_code INT,                         -- Código WMO de clima
    cloud_cover INT,                          -- Cobertura nubosa (%)
    wind_speed_kmh FLOAT,                     -- Velocidad viento (km/h)

    -- Metadata
    raw_json JSONB,                           -- Evento JSON completo
    captured_at TIMESTAMP DEFAULT NOW()       -- Timestamp de inserción
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_city ON raw_weather_events(city);
CREATE INDEX IF NOT EXISTS idx_region ON raw_weather_events(region);
```

**Tipos de Datos**:
- `SERIAL`: Auto-incrementing integer (1, 2, 3, ...)
- `VARCHAR(n)`: String de longitud variable máxima n
- `INT`: Integer de 32 bits
- `FLOAT`: Punto flotante de 64 bits
- `BOOLEAN`: true/false
- `JSONB`: JSON binario (más eficiente que JSON)
- `TIMESTAMP`: Fecha y hora

**Constraints**:
- `PRIMARY KEY`: Identifica únicamente cada fila
- `UNIQUE`: No permite duplicados en `event_id`
- `DEFAULT NOW()`: Valor por defecto es timestamp actual

**Índices**:
- `idx_city`: Acelera queries como `WHERE city = 'Lima'`
- `idx_region`: Acelera queries como `WHERE region = 'Latam'`

---

### Configuration: `.env`

```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092    # Host para acceso desde host machine
KAFKA_TOPIC=weather-events                # Topic name

# PostgreSQL Configuration
POSTGRES_HOST=localhost                   # Host para acceso desde host machine
POSTGRES_PORT=5432                        # Puerto estándar de PostgreSQL
POSTGRES_DB=weather_db                    # Nombre de la base de datos
POSTGRES_USER=kafka_user                  # Usuario de BD
POSTGRES_PASSWORD=kafka123                # Contraseña (cambiar en producción)
```

**Nota**: Dentro de Docker network, los hosts cambian:
- `KAFKA_BOOTSTRAP_SERVERS=kafka:29092`
- `POSTGRES_HOST=postgres`

Estos valores se sobrescriben en `docker-compose.yml` para servicios containerizados.

---

### Docker Configuration: `docker-compose.yml`

#### Servicio: Zookeeper

```yaml
zookeeper:
  image: confluentinc/cp-zookeeper:7.5.0
  container_name: zookeeper
  environment:
    ZOOKEEPER_CLIENT_PORT: 2181
    ZOOKEEPER_TICK_TIME: 2000
  ports:
    - "2181:2181"
```

**Función**: Coordinación del cluster de Kafka

#### Servicio: Kafka

```yaml
kafka:
  image: confluentinc/cp-kafka:7.5.0
  container_name: kafka
  depends_on:
    - zookeeper
  ports:
    - "9092:9092"
  environment:
    KAFKA_BROKER_ID: 1
    KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
    KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INTERNAL:PLAINTEXT,EXTERNAL:PLAINTEXT
    KAFKA_LISTENERS: INTERNAL://0.0.0.0:29092,EXTERNAL://0.0.0.0:9092
    KAFKA_ADVERTISED_LISTENERS: INTERNAL://kafka:29092,EXTERNAL://localhost:9092
    KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
```

**Listeners**:
- `INTERNAL:29092`: Para comunicación entre contenedores
- `EXTERNAL:9092`: Para acceso desde host machine

#### Servicio: PostgreSQL

```yaml
postgres:
  image: postgres:15
  container_name: postgres
  restart: always
  environment:
    POSTGRES_USER: kafka_user
    POSTGRES_PASSWORD: kafka123
    POSTGRES_DB: weather_db
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./init.sql:/docker-entrypoint-initdb.d/init.sql
```

**Volumen**:
- `postgres_data`: Persiste datos entre reinicios
- `init.sql`: Se ejecuta al crear el contenedor

#### Servicio: Airflow Webserver

```yaml
airflow-webserver:
  build:
    context: .
    dockerfile: Dockerfile.airflow
  container_name: airflow-webserver
  command: bash -c "airflow db migrate && airflow users create --username airflow --firstname Airflow --lastname Admin --role Admin --email admin@example.com --password airflow || true && exec airflow webserver"
  ports:
    - "8081:8080"
  environment:
    - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    - AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://kafka_user:kafka123@postgres/weather_db
    - AIRFLOW_CONN_POSTGRES_DEFAULT=postgresql://kafka_user:kafka123@postgres:5432/weather_db
  volumes:
    - ./dags:/opt/airflow/dags
    - ./producers:/opt/airflow/producers
    - ./consumers:/opt/airflow/consumers
```

**Volúmenes**: Hot-reload de código sin rebuild

---

## Base de Datos

### Conexión a PostgreSQL

#### Desde Host Machine

```bash
# Usando psql
psql -h localhost -p 5432 -U kafka_user -d weather_db
# Password: kafka123

# Usando pgAdmin
# URL: http://localhost:5050
# Email: admin@admin.com
# Password: admin
```

#### Desde Contenedor Docker

```bash
# Abrir shell en contenedor
docker exec -it postgres bash

# Conectar con psql
psql -U kafka_user -d weather_db

# O en un solo comando
docker exec -it postgres psql -U kafka_user -d weather_db
```

### Comandos SQL Útiles

#### Exploración de Esquema

```sql
-- Listar todas las tablas
\dt

-- Describir una tabla
\d raw_weather_events
\d analytics_weather

-- Ver índices
\di

-- Ver tamaño de tablas
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public';
```

#### Consultas de Datos Raw

```sql
-- Ver últimos 10 eventos
SELECT
    city,
    temperature_2m,
    relative_humidity_2m,
    captured_at
FROM raw_weather_events
ORDER BY captured_at DESC
LIMIT 10;

-- Contar eventos por ciudad
SELECT
    city,
    COUNT(*) as event_count
FROM raw_weather_events
GROUP BY city
ORDER BY event_count DESC;

-- Ver eventos de las últimas 24 horas
SELECT
    city,
    AVG(temperature_2m) as avg_temp,
    COUNT(*) as records
FROM raw_weather_events
WHERE captured_at >= NOW() - INTERVAL '24 hours'
GROUP BY city;

-- Buscar eventos con precipitación
SELECT
    city,
    precipitation_mm,
    captured_at
FROM raw_weather_events
WHERE precipitation_mm > 0
ORDER BY precipitation_mm DESC;

-- Ver rango de temperaturas por región
SELECT
    region,
    MIN(temperature_2m) as min_temp,
    MAX(temperature_2m) as max_temp,
    AVG(temperature_2m) as avg_temp
FROM raw_weather_events
GROUP BY region;
```

#### Consultas de Analytics

```sql
-- Ver todas las métricas agregadas
SELECT * FROM analytics_weather
ORDER BY avg_temperature DESC;

-- Ciudades más calientes
SELECT
    city,
    avg_temperature,
    max_temperature
FROM analytics_weather
ORDER BY avg_temperature DESC
LIMIT 5;

-- Ciudades más húmedas
SELECT
    city,
    avg_humidity,
    total_precipitation
FROM analytics_weather
ORDER BY avg_humidity DESC;

-- Ciudades con más precipitación
SELECT
    city,
    total_precipitation,
    record_count
FROM analytics_weather
WHERE total_precipitation > 0
ORDER BY total_precipitation DESC;
```

#### Análisis Avanzado

```sql
-- Tendencia de temperatura por hora
SELECT
    city,
    DATE_TRUNC('hour', captured_at) as hour,
    AVG(temperature_2m) as avg_temp
FROM raw_weather_events
WHERE city = 'Ciudad de México'
    AND captured_at >= NOW() - INTERVAL '7 days'
GROUP BY city, hour
ORDER BY hour DESC;

-- Correlación temperatura-humedad
SELECT
    city,
    CORR(temperature_2m, relative_humidity_2m) as correlation
FROM raw_weather_events
GROUP BY city;

-- Detectar anomalías (temperaturas extremas)
SELECT
    city,
    temperature_2m,
    captured_at
FROM raw_weather_events
WHERE temperature_2m < 0 OR temperature_2m > 40
ORDER BY temperature_2m DESC;
```

### Mantenimiento de Base de Datos

#### Limpieza de Datos Antiguos

```sql
-- Eliminar eventos más antiguos de 30 días
DELETE FROM raw_weather_events
WHERE captured_at < NOW() - INTERVAL '30 days';

-- Ver espacio liberado
VACUUM FULL raw_weather_events;
```

#### Backup y Restore

```bash
# Backup
docker exec postgres pg_dump -U kafka_user weather_db > backup.sql

# Restore
docker exec -i postgres psql -U kafka_user -d weather_db < backup.sql

# Backup solo datos (sin esquema)
docker exec postgres pg_dump -U kafka_user -a weather_db > data_only.sql

# Backup en formato custom (comprimido)
docker exec postgres pg_dump -U kafka_user -Fc weather_db > backup.dump
```

#### Verificar Integridad

```sql
-- Verificar duplicados de event_id
SELECT event_id, COUNT(*)
FROM raw_weather_events
GROUP BY event_id
HAVING COUNT(*) > 1;

-- Verificar datos nulos en campos críticos
SELECT COUNT(*)
FROM raw_weather_events
WHERE temperature_2m IS NULL
   OR city IS NULL;

-- Verificar rangos de datos
SELECT
    COUNT(*) FILTER (WHERE temperature_2m < -50 OR temperature_2m > 60) as invalid_temps,
    COUNT(*) FILTER (WHERE relative_humidity_2m < 0 OR relative_humidity_2m > 100) as invalid_humidity,
    COUNT(*) FILTER (WHERE precipitation_mm < 0) as invalid_precip
FROM raw_weather_events;
```

---

## Orquestación con Airflow

### Acceso a Airflow UI

**URL**: http://localhost:8081
**Credenciales**:
- Usuario: `airflow`
- Contraseña: `airflow`

### Activar el DAG

1. Navegar a la vista principal de DAGs
2. Buscar `weather_elt_pipeline`
3. Click en el toggle (interruptor) para activarlo
4. El DAG comenzará a ejecutarse según su schedule (`@hourly`)

### Ejecutar DAG Manualmente

1. En la lista de DAGs, localizar `weather_elt_pipeline`
2. Click en el botón de "Play" (▶) a la derecha
3. Se abrirá un modal
4. Click en "Trigger DAG"
5. Ver progreso en tiempo real

### Monitorear Ejecución

#### Graph View

1. Click en el nombre del DAG
2. Seleccionar "Graph" tab
3. Ver visualización de tasks y sus estados:
   - **Verde**: Success
   - **Rojo**: Failed
   - **Amarillo**: Running
   - **Naranja**: Up for retry
   - **Gris**: Queued
   - **Blanco**: No status

#### Tree View

- Vista cronológica de todas las ejecuciones
- Cada columna es una ejecución (DAG run)
- Cada fila es una task
- Colores indican estado

#### Logs de Tasks

1. En Graph View, click en una task
2. Click en "Log" button
3. Ver stdout/stderr completo
4. Buscar errores o warnings

### Comandos CLI de Airflow

```bash
# Listar todos los DAGs
docker exec airflow-webserver airflow dags list

# Ver estado de un DAG específico
docker exec airflow-webserver airflow dags state weather_elt_pipeline

# Trigger manual de un DAG
docker exec airflow-webserver airflow dags trigger weather_elt_pipeline

# Pausar un DAG
docker exec airflow-webserver airflow dags pause weather_elt_pipeline

# Reanudar un DAG
docker exec airflow-webserver airflow dags unpause weather_elt_pipeline

# Ver últimas ejecuciones
docker exec airflow-webserver airflow dags list-runs -d weather_elt_pipeline

# Test de una task específica
docker exec airflow-webserver airflow tasks test weather_elt_pipeline produce_weather_to_kafka 2025-12-05

# Ver errores de parsing
docker exec airflow-webserver airflow dags list-import-errors
```

### Variables y Connections

#### Ver Variables

```bash
docker exec airflow-webserver airflow variables list
```

#### Ver Connections

```bash
docker exec airflow-webserver airflow connections list
```

### Debugging

#### Error: DAG no aparece

```bash
# Verificar sintaxis del DAG
docker exec airflow-webserver python -m py_compile /opt/airflow/dags/weather_elt_dag.py

# Ver errores de parsing
docker exec airflow-webserver airflow dags list-import-errors

# Revisar logs del scheduler
docker-compose logs airflow-scheduler
```

#### Error: Task falla

1. Ver logs de la task en UI
2. Ejecutar task manualmente para reproducir:
```bash
docker exec airflow-webserver airflow tasks test weather_elt_pipeline produce_weather_to_kafka 2025-12-05
```

3. Verificar conexiones y variables
4. Revisar permisos de archivos

---

## Uso y Comandos

### Ciudades Monitoreadas

El sistema actualmente monitorea 10 ciudades definidas en `data/cities.json`:

| Ciudad | Región | Segmento | Coordenadas |
|--------|--------|----------|-------------|
| Ciudad de México | Latam | Urban | 19.43°N, 99.13°W |
| Madrid | Europa | Premium | 40.41°N, 3.70°W |
| Bogotá | Latam | Urban | 4.61°N, 74.08°W |
| Lima | Latam | Coastal | 12.04°S, 77.02°W |
| Buenos Aires | Latam | Premium | 34.60°S, 58.38°W |
| Santiago | Latam | Urban | 33.45°S, 70.67°W |
| São Paulo | Latam | Premium | 23.55°S, 46.63°W |
| Lisboa | Europa | Coastal | 38.72°N, 9.14°W |
| Miami | Norte | Premium | 25.76°N, 80.19°W |
| La Paz | Latam | Altitude | 16.50°S, 68.15°W |

### Comandos Docker Compose

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de servicios
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f kafka
docker-compose logs -f postgres
docker-compose logs -f airflow-webserver

# Reiniciar un servicio
docker-compose restart kafka

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos)
docker-compose down -v

# Rebuild de imágenes
docker-compose build

# Rebuild y restart
docker-compose up -d --build
```

### Comandos Kafka

```bash
# Listar topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Crear topic manualmente (opcional, auto-create está habilitado)
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic weather-events --partitions 1 --replication-factor 1

# Ver detalles de un topic
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic weather-events

# Ver mensajes de un topic (desde el inicio)
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic weather-events \
  --from-beginning \
  --max-messages 10

# Ver consumer groups
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Ver offset de un consumer group
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group postgres-group --describe

# Eliminar un topic (CUIDADO)
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --delete --topic weather-events
```

### Ejecución Manual de Scripts

#### Modo Desarrollo (fuera de Docker)

```bash
# Activar entorno virtual
source kafka-etl-env/bin/activate  # Linux/macOS
kafka-etl-env\Scripts\activate     # Windows

# Ejecutar producer
python producers/weather_producer.py

# Ejecutar producer en modo batch
python producers/weather_producer.py --batch

# Ejecutar consumer
python consumers/raw_to_postgres.py

# Ejecutar consumer en modo batch
python consumers/raw_to_postgres.py --batch

# Detener con Ctrl+C
```

#### Modo Producción (dentro de Docker)

```bash
# Ejecutar producer en contenedor Airflow
docker exec airflow-webserver python /opt/airflow/producers/weather_producer.py --batch

# Ejecutar consumer en contenedor Airflow
docker exec airflow-webserver python /opt/airflow/consumers/raw_to_postgres.py --batch

# Ejecutar transformación SQL
docker exec -it postgres psql -U kafka_user -d weather_db -f /docker-entrypoint-initdb.d/transform_weather.sql
```

### Verificar Flujo de Datos

#### 1. Verificar Producer → Kafka

```bash
# Ver mensajes en Kafka UI: http://localhost:8080
# O desde CLI:
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic weather-events \
  --from-beginning \
  --max-messages 5
```

#### 2. Verificar Kafka → PostgreSQL

```bash
# Contar registros en tabla raw
docker exec -it postgres psql -U kafka_user -d weather_db \
  -c "SELECT COUNT(*) FROM raw_weather_events;"

# Ver últimos registros
docker exec -it postgres psql -U kafka_user -d weather_db \
  -c "SELECT city, temperature_2m, captured_at FROM raw_weather_events ORDER BY captured_at DESC LIMIT 5;"
```

#### 3. Verificar PostgreSQL → Analytics

```bash
# Ver datos agregados
docker exec -it postgres psql -U kafka_user -d weather_db \
  -c "SELECT * FROM analytics_weather ORDER BY city;"
```

### Dashboard

```bash
# Abrir dashboard en navegador
# Opción 1: Directamente desde archivo
open dashboard/dashboard.html

# Opción 2: Servir con Python
cd dashboard
python -m http.server 8000
# Luego abrir: http://localhost:8000/dashboard.html

# Opción 3: Servir con Node.js
npm install -g http-server
http-server dashboard/
```

---

## Monitoreo y Debugging

### Health Checks

```bash
# Verificar salud de todos los contenedores
docker-compose ps

# Verificar conectividad de PostgreSQL
docker exec -it postgres pg_isready -U kafka_user

# Test de Kafka
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Test de Airflow
curl -I http://localhost:8081/health

# Test de Kafka UI
curl -I http://localhost:8080

# Test de pgAdmin
curl -I http://localhost:5050
```

### Ver Logs

```bash
# Logs en tiempo real de todos los servicios
docker-compose logs -f

# Logs de un servicio específico
docker-compose logs -f kafka
docker-compose logs -f postgres
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver

# Últimas 100 líneas
docker-compose logs --tail=100 kafka

# Logs desde timestamp
docker-compose logs --since 2025-12-05T10:00:00 kafka
```

### Monitorear Recursos

```bash
# Ver uso de CPU, memoria, red de todos los contenedores
docker stats

# Ver uso de disco de Docker
docker system df

# Ver volúmenes
docker volume ls

# Inspeccionar un volumen
docker volume inspect visualizationu3_postgres_data
```

### Kafka UI Monitoring

**URL**: http://localhost:8080

Puedes monitorear:
- **Topics**: Ver todos los topics, configuración, particiones
- **Messages**: Examinar mensajes en cada topic
- **Consumer Groups**: Ver offsets, lag, miembros del grupo
- **Brokers**: Estado del cluster
- **Schema Registry**: Si está configurado

### pgAdmin Monitoring

**URL**: http://localhost:5050
**Login**: admin@admin.com / admin

Puedes:
- Ejecutar queries SQL personalizadas
- Ver estadísticas de tablas
- Monitorear conexiones activas
- Ver logs de PostgreSQL
- Configurar alertas

### Airflow Monitoring

**URL**: http://localhost:8081
**Login**: airflow / airflow

Puedes:
- Ver estado de DAG runs
- Monitorear duración de tasks
- Ver logs detallados por task
- Configurar alertas de fallos
- Ver métricas de performance

---

## Troubleshooting

### Problema: Servicios no inician

**Síntomas**:
```bash
docker-compose ps
# Muestra servicios con estado "Restarting" o "Exited"
```

**Diagnóstico**:
```bash
# Ver logs de servicio problemático
docker-compose logs servicio_nombre

# Ver últimas líneas
docker-compose logs --tail=50 servicio_nombre
```

**Soluciones**:

1. **Recursos insuficientes**:
```bash
# Aumentar memoria en Docker Desktop
# Settings → Resources → Memory: 6GB+

# O iniciar solo servicios esenciales
docker-compose up -d zookeeper kafka postgres
```

2. **Puerto ya en uso**:
```bash
# Linux/macOS: Ver qué usa el puerto
lsof -i :8080

# Windows: Ver qué usa el puerto
netstat -ano | findstr :8080

# Solución: Cambiar puerto en docker-compose.yml
ports:
  - "8081:8080"  # Cambiar primer número
```

3. **Volúmenes corruptos**:
```bash
# CUIDADO: Esto elimina todos los datos
docker-compose down -v
docker-compose up -d
```

### Problema: Kafka no recibe mensajes

**Diagnóstico**:
```bash
# Verificar que Producer está corriendo
docker-compose logs producer

# Verificar topics
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Intentar ver mensajes
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic weather-events \
  --from-beginning
```

**Soluciones**:

1. **Producer no conecta a Kafka**:
```bash
# Verificar variable de entorno
docker exec airflow-webserver env | grep KAFKA

# Debe mostrar: KAFKA_BOOTSTRAP_SERVERS=kafka:29092
```

2. **Topic no existe**:
```bash
# Crear manualmente
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic weather-events --partitions 1 --replication-factor 1
```

3. **Kafka no está listo**:
```bash
# Esperar 1-2 minutos después de docker-compose up
# Verificar logs
docker-compose logs kafka | grep "started"
```

### Problema: Consumer no escribe a PostgreSQL

**Diagnóstico**:
```bash
# Ver logs del consumer
docker-compose logs airflow-scheduler

# Verificar que tabla existe
docker exec -it postgres psql -U kafka_user -d weather_db -c "\dt"

# Intentar inserción manual
docker exec -it postgres psql -U kafka_user -d weather_db -c "INSERT INTO raw_weather_events (event_id, city, city_id) VALUES ('test', 'Test City', 999);"
```

**Soluciones**:

1. **Consumer no conecta a PostgreSQL**:
```bash
# Verificar variables de entorno
docker exec airflow-webserver env | grep POSTGRES

# Deben mostrar:
# POSTGRES_HOST=postgres
# POSTGRES_DB=weather_db
# POSTGRES_USER=kafka_user
```

2. **Tabla no existe**:
```bash
# Ejecutar init.sql manualmente
docker exec -it postgres psql -U kafka_user -d weather_db -f /docker-entrypoint-initdb.d/init.sql
```

3. **Error de permisos**:
```bash
# Verificar permisos del usuario
docker exec -it postgres psql -U kafka_user -d weather_db -c "\du"

# Otorgar permisos
docker exec -it postgres psql -U postgres -d weather_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kafka_user;"
```

### Problema: Airflow DAG no aparece

**Diagnóstico**:
```bash
# Ver errores de parsing
docker exec airflow-webserver airflow dags list-import-errors

# Verificar sintaxis de DAG
docker exec airflow-webserver python -m py_compile /opt/airflow/dags/weather_elt_dag.py

# Ver logs del scheduler
docker-compose logs airflow-scheduler
```

**Soluciones**:

1. **Error de sintaxis**:
```bash
# Corregir el archivo dags/weather_elt_dag.py
# El scheduler detectará automáticamente los cambios
```

2. **DAG pausado por defecto**:
```bash
# Activar desde UI o CLI
docker exec airflow-webserver airflow dags unpause weather_elt_pipeline
```

3. **Scheduler no corriendo**:
```bash
# Reiniciar scheduler
docker-compose restart airflow-scheduler

# Verificar estado
docker-compose ps airflow-scheduler
```

### Problema: Dashboard no muestra datos

**Diagnóstico**:
```bash
# Verificar que tabla analytics tiene datos
docker exec -it postgres psql -U kafka_user -d weather_db \
  -c "SELECT COUNT(*) FROM analytics_weather;"

# Ver datos
docker exec -it postgres psql -U kafka_user -d weather_db \
  -c "SELECT * FROM analytics_weather LIMIT 5;"
```

**Soluciones**:

1. **Tabla analytics vacía**:
```bash
# Ejecutar transformación manualmente
docker exec -it postgres psql -U kafka_user -d weather_db \
  -f /opt/airflow/dags/sql/transform_weather.sql

# O trigger DAG de Airflow
```

2. **Dashboard no conecta a PostgreSQL**:
```html
<!-- Verificar configuración de conexión en dashboard.html -->
<!-- Debe usar: localhost:5432 -->
```

3. **CORS issues**:
```bash
# Servir dashboard con servidor HTTP
cd dashboard
python -m http.server 8000
# Abrir: http://localhost:8000/dashboard.html
```

### Problema: Error "No space left on device"

**Solución**:
```bash
# Limpiar imágenes y contenedores no usados
docker system prune -a

# Limpiar volúmenes no usados
docker volume prune

# Ver uso de espacio
docker system df
```

### Problema: Cambios en código no se reflejan

**Solución**:
```bash
# Para cambios en producers/consumers (montados como volúmenes):
# No requiere acción, se aplican automáticamente

# Para cambios en Dockerfile o requirements:
docker-compose down
docker-compose build
docker-compose up -d

# Para cambios en DAGs:
# Se aplican automáticamente (Airflow escanea cada 30 segundos)
```

### Logs de Debugging Útiles

```bash
# Ver todos los errores en logs
docker-compose logs | grep -i error

# Ver warnings
docker-compose logs | grep -i warn

# Ver conexiones rechazadas
docker-compose logs | grep -i "connection refused"

# Ver timeout errors
docker-compose logs | grep -i timeout

# Exportar logs a archivo
docker-compose logs > debug.log
```

---

## Desarrollo Futuro

### Features Planeados

- [ ] Implementar alertas de clima extremo vía email/SMS
- [ ] Dashboard en tiempo real con WebSockets
- [ ] API REST para consulta de datos históricos
- [ ] Predicciones meteorológicas con Machine Learning
- [ ] Soporte para más ciudades (escalable a 100+)
- [ ] Particionamiento de tablas por fecha
- [ ] Réplicas de Kafka para alta disponibilidad
- [ ] Métricas de calidad de datos (data quality monitoring)
- [ ] Integración con servicios de visualización (Grafana, Superset)
- [ ] Export de datos a formatos CSV, JSON, Parquet

### Optimizaciones

- [ ] Batch processing en consumer (insertar múltiples rows)
- [ ] Compresión de mensajes en Kafka
- [ ] Índices adicionales en PostgreSQL
- [ ] Materializar vistas para queries frecuentes
- [ ] Caché de resultados de analytics
- [ ] Paralelización de producer (múltiples threads)
- [ ] Particionamiento de topic por región

---

## Contribuciones

Este proyecto fue desarrollado como parte del curso de **Visualización U3**.

### Equipo

- Desarrollo del pipeline ETL
- Configuración de infraestructura Docker
- Implementación de transformaciones SQL
- Desarrollo del dashboard

---

## Licencia

Proyecto educativo - Universidad

---

## Contacto y Soporte

Para preguntas, issues o sugerencias:
- **Repositorio**: https://github.com/damapech1/visualizationU3
- **Issues**: https://github.com/damapech1/visualizationU3/issues

---

## Referencias y Recursos

### Documentación Oficial

- **Apache Kafka**: https://kafka.apache.org/documentation/
- **Apache Airflow**: https://airflow.apache.org/docs/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Confluent Kafka Python**: https://docs.confluent.io/kafka-clients/python/current/overview.html
- **Open-Meteo API**: https://open-meteo.com/en/docs

### Tutoriales

- **Kafka Basics**: https://kafka.apache.org/quickstart
- **Airflow Tutorial**: https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html
- **Docker Compose**: https://docs.docker.com/compose/

### Tools

- **Kafka UI**: https://github.com/provectus/kafka-ui
- **pgAdmin**: https://www.pgadmin.org/docs/
- **DBeaver**: https://dbeaver.io/ (alternativa a pgAdmin)

---

**Última actualización**: Diciembre 2025

**Versión del proyecto**: 1.0.0
