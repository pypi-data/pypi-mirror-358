import argparse
from db import connect, get_table_names, fetch_table_data, close_connection
from utils import infer_type
from sqlalchemy import text

# For safe type checking
def is_type(value, expected_type):
    try:
        if expected_type == "datetime":
            import pandas as pd
            return pd.to_datetime(value, errors="coerce") is not pd.NaT
        return isinstance(value, expected_type)
    except:
        return False

# Mapping to SQL types for ALTER command
def get_sql_type(py_type, db_engine_name):
    mapping = {
        "mysql": {
            bool: "BOOLEAN",
            int: "INT",
            float: "FLOAT",
            str: "VARCHAR(255)",
            "datetime": "DATETIME"
        },
        "postgresql": {
            bool: "BOOLEAN",
            int: "INTEGER",
            float: "REAL",
            str: "VARCHAR",
            "datetime": "TIMESTAMP"
        }
    }
    return mapping[db_engine_name].get(py_type, "TEXT")

def run_type_check_and_fix(db_url, dry_run=True):
    engine, session = connect(db_url)
    db_type = engine.dialect.name  # mysql or postgresql
    tables = get_table_names(engine)

    print(f"\n--- {'DRY RUN' if dry_run else 'APPLYING FIXES'}: {db_type.upper()} ---")
    mismatches = []

    for table in tables:
        records = fetch_table_data(session, table)
        if not records:
            continue

        # Collect sample values for each column
        column_samples = {}
        for record in records:
            for key, val in record.items():
                if key not in column_samples:
                    column_samples[key] = []
                if val is not None:
                    column_samples[key].append(val)

        for column_name, values in column_samples.items():
            result = infer_type(column_name, values[:20])
            expected_type = result["final_inferred_type"]

            for row in records:
                val = row.get(column_name)
                if val is not None and not is_type(val, expected_type):
                    mismatches.append((table, column_name, type(val).__name__, expected_type))
                    if dry_run:
                        break
                    else:
                        try:
                            sql_type = get_sql_type(expected_type, db_type)
                            alter_stmt = text(f'ALTER TABLE "{table}" ALTER COLUMN "{column_name}" TYPE {sql_type}') \
                                if db_type == "postgresql" else \
                                text(f'ALTER TABLE `{table}` MODIFY COLUMN `{column_name}` {sql_type}')
                            session.execute(alter_stmt)
                            print(f"[APPLIED] {table}.{column_name} changed to {sql_type}")
                            session.commit()
                        except Exception as e:
                            print(f"[ERROR] Failed to alter {table}.{column_name}: {e}")
                    break

    if dry_run:
        if mismatches:
            print("🔍 The following columns need type changes:\n")
            for table, column, found, expected in mismatches:
                print(f"Table: {table}\n  - Column '{column}': found {found}, expected {expected.__name__ if isinstance(expected, type) else expected}")
        else:
            print("✅ No mismatches found.")

    close_connection(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect and fix column datatype mismatches in DB.")
    parser.add_argument("--db_url", type=str, required=True, help="Database URL (SQLAlchemy format)")
    parser.add_argument("--dry_run", type=lambda x: x.lower() == 'true', default=True, help="Dry run mode (true/false)")

    args = parser.parse_args()
    run_type_check_and_fix(args.db_url, args.dry_run)
