# PostgreSQL Cluster with Replication using Docker Compose

This repository provides a setup for a PostgreSQL cluster with a primary (master) node and one replica (standby) node using Docker Compose. This setup ensures data redundancy and increases data availability.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Setup Instructions](#setup-instructions)
    - [1. Create the Docker Compose File](#1-create-the-docker-compose-file)
    - [2. Create Replication Initialization Scripts](#2-create-replication-initialization-scripts)
    - [3. Bring Up the Cluster](#3-bring-up-the-cluster)
4. [How Replication Works](#how-replication-works)
5. [Monitoring and Failover](#monitoring-and-failover)
6. [License](#license)

## Introduction

This setup uses streaming replication to keep the replica in sync with the primary. Streaming replication ensures that changes made to the primary database are immediately replicated to the standby, providing high availability and data redundancy.

## Prerequisites

- Docker
- Docker Compose

## Setup Instructions

### 1. Create the Docker Compose File

Create a file named `docker-compose.yml` with the following content:

```yaml
version: '3.8'

services:
  postgres-master:
    image: postgres:16
    container_name: postgres-master
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: rep_password
    volumes:
      - master_data:/var/lib/postgresql/data
      - ./init/master-init.sh:/docker-entrypoint-initdb.d/master-init.sh
    ports:
      - "5432:5432"
    networks:
      - postgres-network

  postgres-replica:
    image: postgres:16
    container_name: postgres-replica
    environment:
      POSTGRES_DB: mydatabase
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD: rep_password
      POSTGRES_MASTER_HOST: postgres-master
    volumes:
      - replica_data:/var/lib/postgresql/data
      - ./init/replica-init.sh:/docker-entrypoint-initdb.d/replica-init.sh
    ports:
      - "5433:5432"
    networks:
      - postgres-network
    depends_on:
      - postgres-master

volumes:
  master_data:
  replica_data:

networks:
  postgres-network:
    driver: bridge
```

### 2. Create Replication Initialization Scripts

Create a directory named `init` and add the following scripts.

#### 2.1. `master-init.sh` for the Master

Create a file named `init/master-init.sh` with the following content:

```sh
#!/bin/bash
set -e

# Start PostgreSQL server
docker-entrypoint.sh postgres &

# Wait for PostgreSQL to start
until pg_isready -h localhost; do
  sleep 1
done

# Create replication user and configure replication
psql -U postgres -c "CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'rep_password';"
psql -U postgres -c "ALTER SYSTEM SET wal_level = replica;"
psql -U postgres -c "ALTER SYSTEM SET max_wal_senders = 10;"
psql -U postgres -c "ALTER SYSTEM SET max_replication_slots = 10;"
psql -U postgres -c "SELECT pg_reload_conf();"

# Create replication slot
psql -U postgres -c "SELECT * FROM pg_create_physical_replication_slot('replica_slot');"

# Keep the container running
tail -f /dev/null
```

#### 2.2. `replica-init.sh` for the Replica

Create a file named `init/replica-init.sh` with the following content:

```sh
#!/bin/bash
set -e

# Wait for the master to be available
until pg_isready -h postgres-master; do
  sleep 1
done

# Stop PostgreSQL server
pg_ctl -D "$PGDATA" -m fast -w stop

# Clean up old data
rm -rf "$PGDATA"/*

# Perform base backup
PGPASSWORD=rep_password pg_basebackup -h postgres-master -D "$PGDATA" -U replicator -v -P --wal-method=stream

# Create recovery.conf
cat <<EOF > "$PGDATA/recovery.conf"
standby_mode = 'on'
primary_conninfo = 'host=postgres-master port=5432 user=replicator password=rep_password'
primary_slot_name = 'replica_slot'
EOF

# Start PostgreSQL server
pg_ctl -D "$PGDATA" -o "-c listen_addresses='*'" -w start

# Keep the container running
tail -f /dev/null
```

### 3. Bring Up the Cluster

Run the following command to bring up your PostgreSQL cluster:

```sh
docker-compose up -d
```

## How Replication Works

Replication in PostgreSQL involves copying data from one database server (the primary) to one or more other database servers (the replicas). This setup ensures data redundancy and increases data availability.

### Primary (Master) Configuration

1. **Configure WAL (Write-Ahead Logging) Settings:**
   - `wal_level = replica`
   - `max_wal_senders = 10`
   - `max_replication_slots = 10`

2. **Create a Replication User:**
   - `CREATE USER replicator REPLICATION LOGIN ENCRYPTED PASSWORD 'rep_password';`

3. **Create Replication Slots:**
   - `SELECT * FROM pg_create_physical_replication_slot('replica_slot');`

### Replica (Standby) Configuration

1. **Base Backup:**
   - Perform a base backup of the primary server.

2. **Streaming Replication Configuration:**
   - Configure the `primary_conninfo` parameter and create a `recovery.conf` file on the replica.

### Streaming Replication Process

1. **Write-Ahead Logging (WAL) on Primary:**
   - WAL ensures that changes can be replayed to maintain data integrity.

2. **Streaming WAL Data:**
   - The primary server streams the WAL data to the replica servers in real-time.

3. **Applying WAL Data on Replica:**
   - The replica server receives the WAL data and applies it to its local database.

## Monitoring and Failover

- **Monitoring:**
  - Use `pg_stat_replication` and `pg_stat_wal_receiver` views to monitor the replication status.

- **Failover:**
  - In case of primary failure, promote a replica to primary manually or using tools like `repmgr` or `Patroni`.

## License

This project is licensed under the MIT License.