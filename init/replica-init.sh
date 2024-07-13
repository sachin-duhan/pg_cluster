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
cat <<EOF2 > "$PGDATA/recovery.conf"
standby_mode = 'on'
primary_conninfo = 'host=postgres-master port=5432 user=replicator password=rep_password'
primary_slot_name = 'replica_slot'
EOF2

# Start PostgreSQL server
pg_ctl -D "$PGDATA" -o "-c listen_addresses='*'" -w start

# Keep the container running
tail -f /dev/null
