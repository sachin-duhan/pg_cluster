# PostgreSQL Cluster with Replication

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

Create a file named `docker-compose.yml` with the necessary configuration for the primary (master) and replica (standby) nodes.

### 2. Create Replication Initialization Scripts

Create a directory named `init` and add the initialization scripts for both the master and replica nodes.

### 3. Bring Up the Cluster

Run the following command to bring up your PostgreSQL cluster:

```sh
docker-compose up -d
```

## How Replication Works

Replication in PostgreSQL involves copying data from one database server (the primary) to one or more other database servers (the replicas). This setup ensures data redundancy and increases data availability.

### Primary (Master) Configuration

1. **Configure WAL (Write-Ahead Logging) Settings:**
   - Set appropriate `wal_level`, `max_wal_senders`, and `max_replication_slots`.

2. **Create a Replication User:**
   - Create a user with replication privileges.

3. **Create Replication Slots:**
   - Create the necessary replication slots.

### Replica (Standby) Configuration

1. **Base Backup:**
   - Perform a base backup of the primary server.

2. **Streaming Replication Configuration:**
   - Configure the `primary_conninfo` parameter and create the necessary signal files on the replica.

### Streaming Replication Process

1. **Write-Ahead Logging (WAL) on Primary:**
   - WAL ensures that changes can be replayed to maintain data integrity.

2. **Streaming WAL Data:**
   - The primary server streams the WAL data to the replica servers in real-time.

3. **Applying WAL Data on Replica:**
   - The replica server receives the WAL data and applies it to its local database.

## Monitoring and Failover

- **Monitoring:**
  - Use PostgreSQL views such as `pg_stat_replication` and `pg_stat_wal_receiver` to monitor the replication status.

- **Failover:**
  - In case of primary failure, promote a replica to primary manually or using tools like `repmgr` or `Patroni`.

## License

This project is licensed under the MIT License.