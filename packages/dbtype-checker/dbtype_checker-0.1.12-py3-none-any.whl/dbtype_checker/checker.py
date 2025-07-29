from .db import connect, get_table_names, fetch_table_data, close_connection
from .utils import infer_type
from sqlalchemy import text


def is_type(value, expected_type):
    try:
        if expected_type == "datetime":
            import pandas as pd
            return pd.to_datetime(value, errors="coerce") is not pd.NaT
        return isinstance(value, expected_type)
    except:
        return False


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


def check_column_types(db_url):
    engine, session = connect(db_url)
    tables = get_table_names(engine)
    mismatches = []

    for table in tables:
        records = fetch_table_data(session, table)
        if not records:
            continue

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
                    mismatches.append((
                        table,
                        column_name,
                        type(val).__name__,
                        expected_type.__name__ if isinstance(expected_type, type) else str(expected_type)
                    ))
                    break

    close_connection(session)
    return mismatches


def print_mismatches(db_url):
    mismatches = check_column_types(db_url)

    if mismatches:
        print("\nMismatched column types found:")
        for table, column, found, expected in mismatches:
            print(f" - {table}.{column}: found {found}, expected {expected}")
    else:
        print("No mismatches found.")


def run_type_check_and_fix(db_url, dry_run=True):
    engine, session = connect(db_url)
    db_type = engine.dialect.name
    tables = get_table_names(engine)

    print(f"\n--- {'DRY RUN' if dry_run else 'APPLYING FIXES'}: {db_type.upper()} ---")
    mismatches = []

    for table in tables:
        records = fetch_table_data(session, table)
        if not records:
            continue

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

                    if not dry_run:
                        try:
                            sql_type = get_sql_type(expected_type, db_type)

                            # --- DATA PRE-CLEAN STEP ---
                            if db_type == "mysql":
                                if expected_type == bool:
                                    session.execute(text(f"""
                                        UPDATE `{table}` SET `{column_name}` = 
                                            CASE 
                                                WHEN LOWER(`{column_name}`) IN ('true', 'yes', '1') THEN 1 
                                                WHEN LOWER(`{column_name}`) IN ('false', 'no', '0') THEN 0 
                                                ELSE NULL 
                                            END
                                    """))
                                elif expected_type == int:
                                    session.execute(text(f"""
                                        UPDATE `{table}` SET `{column_name}` = 
                                            CASE 
                                                WHEN `{column_name}` REGEXP '^-?[0-9]+$' THEN `{column_name}`
                                                ELSE NULL 
                                            END
                                    """))
                                elif expected_type == float:
                                    session.execute(text(f"""
                                        UPDATE `{table}` SET `{column_name}` = 
                                            CASE 
                                                WHEN `{column_name}` REGEXP '^-?[0-9]*\\.?[0-9]+$' THEN `{column_name}`
                                                ELSE NULL 
                                            END
                                    """))
                                session.commit()

                            elif db_type == "postgresql":
                                if expected_type == bool:
                                    session.execute(text(f"""
                                        UPDATE "{table}" SET "{column_name}" = 
                                            CASE 
                                                WHEN LOWER("{column_name}") IN ('true', 'yes', '1') THEN 'true'
                                                WHEN LOWER("{column_name}") IN ('false', 'no', '0') THEN 'false'
                                                ELSE NULL 
                                            END
                                    """))
                                elif expected_type == int:
                                    session.execute(text(f"""
                                        UPDATE "{table}" SET "{column_name}" = 
                                            CASE 
                                                WHEN "{column_name}" ~ '^-?\\d+$' THEN "{column_name}"
                                                ELSE NULL 
                                            END
                                    """))
                                elif expected_type == float:
                                    session.execute(text(f"""
                                        UPDATE "{table}" SET "{column_name}" = 
                                            CASE 
                                                WHEN "{column_name}" ~ '^[-+]?\\d*\\.?\\d+$' THEN "{column_name}"
                                                ELSE NULL 
                                            END
                                    """))
                                session.commit()
                            # --- END DATA CLEAN ---

                            # --- APPLY ALTER STATEMENT ---
                            if db_type == "postgresql":
                                if expected_type == bool:
                                    alter_stmt = text(f'''
                                        ALTER TABLE "{table}" 
                                        ALTER COLUMN "{column_name}" TYPE BOOLEAN 
                                        USING CASE 
                                            WHEN LOWER("{column_name}") IN ('true', 'yes', '1') THEN TRUE
                                            WHEN LOWER("{column_name}") IN ('false', 'no', '0') THEN FALSE
                                            ELSE NULL
                                        END
                                    ''')
                                else:
                                    alter_stmt = text(f'''
                                        ALTER TABLE "{table}" 
                                        ALTER COLUMN "{column_name}" TYPE {sql_type} 
                                        USING "{column_name}"::{sql_type}
                                    ''')
                            else:
                                alter_stmt = text(
                                    f'ALTER TABLE `{table}` MODIFY COLUMN `{column_name}` {sql_type}'
                                )

                            session.execute(alter_stmt)
                            session.commit()
                            print(f"[APPLIED] {table}.{column_name} changed to {sql_type}")

                        except Exception as e:
                            session.rollback()
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
