import os
import duckdb
from warehouse.db_connection import get_connection, initialize_schema

def load_all_csvs_to_warehouse(csv_dir="data/synthetic/", db_path="clara.db"):
    """
    Bulk loads generated synthetic CSV files into the DuckDB warehouse using native fast loading patterns.
    Ensures safe re-runnability by truncating existing data.

    Parameters:
        csv_dir (str): Relative path to directory containing synthetic CSVs. Defaults to "data/synthetic/".
        db_path (str): Relative filename of the database. Defaults to "clara.db".
    """
    # 1. Establish connection and initialize schema
    conn = get_connection(db_path)
    initialize_schema(conn)

    # 2. Resolve CSV paths relative to project root
    if not os.path.isabs(csv_dir):
        warehouse_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(warehouse_dir)
        full_csv_dir = os.path.abspath(os.path.join(project_root, csv_dir))
    else:
        full_csv_dir = os.path.abspath(csv_dir)

    tables_and_csvs = [
        ("cloud_instances", "instances.csv"),
        ("security_configurations", "security_configs.csv"),
        ("metrics_daily", "metrics.csv"),
        ("cost_data", "cost_data.csv"),
        ("security_events", "security_events.csv")
    ]

    try:
        # 3. Truncate existing data in reverse dependency order to avoid foreign key errors
        print("DataLoader: Cleaning existing table records...")
        conn.execute("DELETE FROM recommendations")
        conn.execute("DELETE FROM risk_scores")
        conn.execute("DELETE FROM security_events")
        conn.execute("DELETE FROM cost_data")
        conn.execute("DELETE FROM metrics_daily")
        conn.execute("DELETE FROM security_configurations")
        conn.execute("DELETE FROM cloud_instances")

        # 4. Ingest data in correct dependency order (instances first)
        for table_name, csv_name in tables_and_csvs:
            csv_path = os.path.join(full_csv_dir, csv_name).replace("\\", "/")
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Required CSV not found at: {csv_path}")

            print(f"DataLoader: Bulk importing {csv_name} into table {table_name}...")
            # Use native fast bulk loading
            conn.execute(f"INSERT INTO {table_name} SELECT * FROM read_csv_auto('{csv_path}')")

        # 5. Validation counts check
        print("\nDataLoader Ingestion Summary:")
        for table_name, _ in tables_and_csvs:
            count_res = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            print(f"Loaded {table_name}: {count_res[0]} rows")

    except Exception as e:
        print(f"DataLoader: Ingestion failed with error: {e}")
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    load_all_csvs_to_warehouse()
