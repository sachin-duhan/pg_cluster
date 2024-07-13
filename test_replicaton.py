import psycopg2
import time

# Connection strings
master_conn_str = "postgresql://postgres:postgres@localhost:5432/mydatabase"
replica_conn_str = "postgresql://postgres:postgres@localhost:5433/mydatabase"

# Function to create table if it doesn't exist
def create_table(conn_str):
    try:
        conn = psycopg2.connect(conn_str)
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS replication_test (
            id SERIAL PRIMARY KEY,
            data TEXT
        );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Table replication_test is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")

# Insert data into the master
def insert_data():
    try:
        conn = psycopg2.connect(master_conn_str)
        cur = conn.cursor()
        cur.execute("INSERT INTO replication_test (data) VALUES (%s) RETURNING id;", ('Test replication data',))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        print(f"Inserted data with ID {inserted_id} into the master.")
        return inserted_id
    except Exception as e:
        print(f"Error inserting data into master: {e}")

# Check data in the replica
def check_data(inserted_id):
    try:
        conn = psycopg2.connect(replica_conn_str)
        cur = conn.cursor()
        cur.execute("SELECT id, data FROM replication_test WHERE id = %s;", (inserted_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            print(f"Data found in replica: ID = {row[0]}, data = {row[1]}")
        else:
            print("Data not found in replica.")
    except Exception as e:
        print(f"Error checking data in replica: {e}")

if __name__ == "__main__":
    # Ensure the table exists on the master
    create_table(master_conn_str)
    
    # Insert data into the master and wait for replication
    inserted_id = insert_data()
    time.sleep(1)  # Wait for replication to occur

    # Ensure the table exists on the replica (shouldn't be necessary if replication is working)
    create_table(replica_conn_str)

    # Check if the data is replicated
    check_data(inserted_id)
