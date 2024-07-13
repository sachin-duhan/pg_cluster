import psycopg2
import time

# Connection strings
master_conn_str = "postgresql://postgres:postgres@localhost:5432/mydatabase"
replica_conn_str = "postgresql://postgres:postgres@localhost:5433/mydatabase"

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
    inserted_id = insert_data()
    time.sleep(5)  # Wait for replication to occur
    check_data(inserted_id)
