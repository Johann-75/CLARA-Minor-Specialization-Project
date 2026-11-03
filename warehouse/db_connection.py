import os
import duckdb

def get_connection(db_path="clara.db") -> duckdb.DuckDBPyConnection:
    """
    Opens (or creates) a connection to the clara.db database located in the project root.

    Parameters:
        db_path (str): Relative filename of the database. Defaults to "clara.db".

    Returns:
        duckdb.DuckDBPyConnection: The native DuckDB connection.
    """
    # Retrieve the project root directory path
    warehouse_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(warehouse_dir)
    full_path = os.path.join(project_root, db_path)
    
    return duckdb.connect(full_path)

def initialize_schema(conn: duckdb.DuckDBPyConnection):
    """
    Reads and executes warehouse/schema.sql to create necessary tables and indexes.
    Uses CREATE TABLE IF NOT EXISTS semantics.

    Parameters:
        conn (duckdb.DuckDBPyConnection): Active database connection.
    """
    warehouse_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(warehouse_dir, "schema.sql")
    
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_script = f.read()
        
    # Split commands by semicolon to execute individually
    statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
    for statement in statements:
        conn.execute(statement)

    migrate_schema(conn)
    
    print("Database: Schema initialized successfully.")

def migrate_schema(conn: duckdb.DuckDBPyConnection):
    """
    Applies idempotent schema migrations to ensure backward compatibility
    with existing databases. Historical pre-migration records without
    provenance are marked as legacy_unknown.
    """
    migrations = [
        "ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS generation_source VARCHAR DEFAULT 'legacy_unknown'",
        "ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS model_name VARCHAR DEFAULT 'unknown'",
        "ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS fallback_reason VARCHAR DEFAULT 'pre_migration_record'",
        "ALTER TABLE recommendations ADD COLUMN IF NOT EXISTS expected_benefit VARCHAR",
        "UPDATE recommendations SET generation_source = 'legacy_unknown' WHERE generation_source IS NULL",
        "UPDATE recommendations SET model_name = 'unknown' WHERE model_name IS NULL",
        "UPDATE recommendations SET fallback_reason = 'pre_migration_record' WHERE generation_source = 'legacy_unknown' AND fallback_reason IS NULL"
    ]
    for stmt in migrations:
        try:
            conn.execute(stmt)
        except Exception:
            # Tolerant to pre-existing tables or uninitialized tables
            pass
