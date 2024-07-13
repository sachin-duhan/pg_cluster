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
