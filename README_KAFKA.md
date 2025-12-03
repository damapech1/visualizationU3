# visualizationU3
Final Project using kafka + Postgres + Airflow

## 🎯 Overview

This guide will walk you through setting up a complete Kafka environment for learning modern ETL (Extract, Transform, Load) concepts. By the end of this setup, you'll have:

- ✅ **Kafka cluster** running in Docker containers
- ✅ **Web UI** for monitoring topics and messages
- ✅ **Python environment** with all required dependencies
- ✅ **Sample data streams** ready for processing

**Estimated Setup Time**: 20-30 minutes

---

## 📋 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 4 GB | 8 GB+ |
| **CPU** | 2 cores | 4 cores+ |
| **Disk Space** | 2 GB | 5 GB+ |
| **OS** | Windows 10, macOS 10.15, Ubuntu 18.04 | Latest versions |

### Software Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # Verify installation
   docker --version
   docker-compose --version
   ```

2. **Python 3.8+**
   ```bash
   # Verify installation
   python --version  # or python3 --version
   pip --version     # or pip3 --version
   ```

3. **Git** (for cloning repositories)
   ```bash
   git --version
   ```

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Lab Directory

```bash
# Git clone the repositori 
git clone https://github.com/damapech1/visualizationU3.git

# Verify you're in the correct location
ls -la
# Should show: README_KAFKA.md, docker-compose.yml, src/, requirements.txt
```

### Step 2: Create the environment
```bash
# Create virtual environment
python -m venv kafka-etl-env

# Activate virtual environment
# On Linux/macOS:
source kafka-etl-env/bin/activate

# On Windows:
kafka-etl-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Start Kafka Infrastructure

```bash
# Start all services in background
docker-compose up -d

# Verify services are running
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND             STATUS
kafka-broker        "..."               Up (healthy)
kafka-ui            "..."               Up (healthy)  
kafka-zookeeper     "..."               Up (healthy)
postgres            "..."               Up (healthy)
pgadmin             "..."               Up (healthy)         

```

### Step 3: Verify Kafka UI Access

1. Open your web browser
2. Navigate to: http://localhost:8080
3. You should see the Kafka UI dashboard

**If the UI doesn't load**, wait 1-2 minutes for services to fully initialize.


### Step 4: Run consumers and producers
```bash
# 1 Terminal: Run the producer 
python producers/weather_producer.py

# 2 Terminal: Run the consumer
source consumers/raw_to_postgres

# 3 Terminal Verify their information is in the table
docker exec -it postgres psql -U kafka_user -d weather_db
```
### Step 5: Check the database

```sql

-- Check the table name
\dt

-- Select and verify the information
SELECT * FROM name_table;

```