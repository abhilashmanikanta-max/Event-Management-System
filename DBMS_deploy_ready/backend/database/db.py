import os
import re
import sqlite3
from pathlib import Path
from backend.config.config import Config

# Optional oracledb import
try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False


class DatabaseManager:
    """
    Unified Database Manager supporting SQLite and Oracle Database.
    Demonstrates real DBMS connectivity, transactions, parameterized queries,
    and foreign key constraint enforcement.
    """

    def __init__(self):
        self.db_type = Config.DB_TYPE
        self.sqlite_path = Path(Config.SQLITE_DB_PATH)
        # Ensure parent directory exists for SQLite
        self.sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        """Establishes and returns a database connection with foreign keys enabled."""
        if self.db_type == 'oracle':
            if not ORACLE_AVAILABLE:
                raise RuntimeError(
                    "Oracle DB driver 'oracledb' is not installed. Run 'pip install oracledb'."
                )
            
            # Construct DSN
            if Config.ORACLE_SID:
                dsn = oracledb.makedsn(
                    Config.ORACLE_HOST,
                    Config.ORACLE_PORT,
                    sid=Config.ORACLE_SID
                )
            else:
                dsn = f"{Config.ORACLE_HOST}:{Config.ORACLE_PORT}/{Config.ORACLE_SERVICE_NAME}"
            
            try:
                conn = oracledb.connect(
                    user=Config.ORACLE_USER,
                    password=Config.ORACLE_PASSWORD,
                    dsn=dsn
                )
                conn.autocommit = False
                return conn
            except Exception as e:
                raise ConnectionError(
                    f"Failed to connect to Oracle SQL Database at {Config.ORACLE_HOST}:{Config.ORACLE_PORT}. "
                    f"Details: {str(e)}"
                )
        else:
            # Default to SQLite
            conn = sqlite3.connect(str(self.sqlite_path))
            conn.row_factory = sqlite3.Row
            # Enforce foreign key constraints in SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn

    def _convert_query_placeholders(self, query: str) -> str:
        """Converts ? placeholders to :1, :2 for Oracle if in Oracle mode."""
        if self.db_type != 'oracle':
            return query
        
        counter = 0
        def replacer(match):
            nonlocal counter
            counter += 1
            return f":{counter}"
        
        return re.sub(r'\?', replacer, query)

    def _format_error(self, e: Exception) -> str:
        """Translates low-level SQL errors into student/evaluator-friendly explanations."""
        err_msg = str(e)
        err_lower = err_msg.lower()

        if "foreign key constraint failed" in err_lower or "ora-02292" in err_lower:
            return (
                "DBMS Foreign Key Constraint Violation: Cannot delete or update this record "
                "because other dependent records reference it in child tables. Delete or reassign "
                "the dependent records first."
            )
        if "foreign key" in err_lower or "ora-02291" in err_lower:
            return (
                "DBMS Foreign Key Integrity Error: The selected parent record (Organizer, Venue, "
                "Category, Participant, or Event) does not exist in the referenced table."
            )
        if "unique constraint failed" in err_lower or "ora-00001" in err_lower:
            return (
                "DBMS Unique Key Constraint Violation: A record with this email or unique identifier "
                "already exists in the database. Duplicate entries are disallowed."
            )
        if "check constraint failed" in err_lower or "ora-02290" in err_lower:
            return (
                "DBMS Check Constraint Violation: Input value violates table validation rules "
                "(e.g., Capacity must be > 0, Amount must be >= 0, or invalid status string)."
            )
        if "not null constraint failed" in err_lower or "ora-01400" in err_lower:
            return "DBMS Not Null Constraint Violation: One or more required fields are missing."

        return f"Database Error: {err_msg}"

    def fetch_all(self, query: str, params=()):
        """Executes a parameterized SELECT query and returns a list of dictionaries."""
        conn = self.get_connection()
        try:
            converted_query = self._convert_query_placeholders(query)
            cursor = conn.cursor()
            cursor.execute(converted_query, params)

            if self.db_type == 'oracle':
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    record = {}
                    for col_name, val in zip(columns, row):
                        # Convert Oracle types if needed
                        record[col_name] = str(val) if hasattr(val, 'isoformat') else val
                    result.append(record)
                return result
            else:
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise RuntimeError(self._format_error(e)) from e
        finally:
            conn.close()

    def fetch_one(self, query: str, params=()):
        """Executes a query and returns a single row dictionary or None."""
        results = self.fetch_all(query, params)
        return results[0] if results else None

    def execute(self, query: str, params=()):
        """Executes INSERT, UPDATE, DELETE with transaction commit and returns lastrowid and rowcount."""
        conn = self.get_connection()
        try:
            converted_query = self._convert_query_placeholders(query)
            cursor = conn.cursor()
            cursor.execute(converted_query, params)
            conn.commit()

            last_id = getattr(cursor, 'lastrowid', None)
            row_count = cursor.rowcount
            return {"lastrowid": last_id, "rowcount": row_count}
        except Exception as e:
            conn.rollback()
            raise RuntimeError(self._format_error(e)) from e
        finally:
            conn.close()

    def execute_script(self, script_text: str):
        """Executes multiple DDL or DML statements."""
        conn = self.get_connection()
        try:
            if self.db_type == 'oracle':
                cursor = conn.cursor()
                statements = [s.strip() for s in script_text.split(';') if s.strip()]
                for stmt in statements:
                    if stmt.endswith('/'):
                        stmt = stmt[:-1].strip()
                    if stmt:
                        cursor.execute(stmt)
                conn.commit()
            else:
                conn.executescript(script_text)
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise RuntimeError(self._format_error(e)) from e
        finally:
            conn.close()

    def init_database(self, seed: bool = True):
        """Initializes tables and seeds initial data if not already populated."""
        if self.db_type == 'oracle':
            # Oracle setup
            try:
                # Test connection
                conn = self.get_connection()
                conn.close()
                print(f"[DBMS] Connected successfully to Oracle Database at {Config.ORACLE_HOST}")
            except Exception as e:
                print(f"[DBMS Warning] Could not connect to Oracle DB ({e}). Falling back to SQLite.")
                self.db_type = 'sqlite'

        if self.db_type == 'sqlite':
            # Check if tables already exist
            tables = self.get_existing_tables()
            expected_tables = {'Organizer', 'Venue', 'Category', 'Participant', 'Event', 'Registration', 'Payment'}
            
            if not expected_tables.issubset(set(tables)):
                print("[DBMS] Creating SQLite tables from schema DDL...")
                with open(Config.SCHEMA_SQLITE_PATH, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                self.execute_script(schema_sql)

                if seed:
                    print("[DBMS] Populating initial seed data...")
                    with open(Config.SEED_SQLITE_PATH, 'r', encoding='utf-8') as f:
                        seed_sql = f.read()
                    self.execute_script(seed_sql)
                    print("[DBMS] Initial seed data successfully inserted!")
            else:
                print(f"[DBMS] SQLite database verified with {len(tables)} tables.")

    def reset_database(self):
        """Completely drops and recreates schema with fresh seed data."""
        if self.db_type == 'sqlite':
            with open(Config.SCHEMA_SQLITE_PATH, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            with open(Config.SEED_SQLITE_PATH, 'r', encoding='utf-8') as f:
                seed_sql = f.read()

            conn = self.get_connection()
            try:
                conn.execute("PRAGMA foreign_keys = OFF;")
                for tbl in ['Payment', 'Registration', 'Event', 'Participant', 'Category', 'Venue', 'Organizer']:
                    conn.execute(f"DROP TABLE IF EXISTS {tbl};")
                conn.commit()
            finally:
                conn.close()

            self.execute_script(schema_sql)
            self.execute_script(seed_sql)
            return {"status": "success", "message": "Database reset and re-seeded successfully."}
        elif self.db_type == 'oracle':
            with open(Config.SCHEMA_ORACLE_PATH, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            with open(Config.SEED_ORACLE_PATH, 'r', encoding='utf-8') as f:
                seed_sql = f.read()
            self.execute_script(schema_sql)
            self.execute_script(seed_sql)
            return {"status": "success", "message": "Oracle Database reset and re-seeded successfully."}

    def get_existing_tables(self):
        """Returns list of user-created table names in database."""
        if self.db_type == 'oracle':
            query = "SELECT table_name FROM user_tables ORDER BY table_name"
            rows = self.fetch_all(query)
            return [r.get('TABLE_NAME') or r.get('table_name') for r in rows]
        else:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            rows = self.fetch_all(query)
            return [r['name'] for r in rows]

    def get_table_metadata(self, table_name: str):
        """Returns schema columns, types, keys, and row count for a specific table."""
        # Sanitize table_name against known whitelist
        valid_tables = {
            'Organizer': 'Organizer',
            'Event': 'Event',
            'Venue': 'Venue',
            'Category': 'Category',
            'Participant': 'Participant',
            'Registration': 'Registration',
            'Payment': 'Payment'
        }
        
        canonical_name = None
        for key in valid_tables:
            if key.lower() == table_name.lower():
                canonical_name = key
                break

        if not canonical_name:
            raise ValueError(f"Table '{table_name}' is not recognized in Event Management System schema.")

        # Total row count
        count_res = self.fetch_one(f"SELECT COUNT(*) AS total FROM {canonical_name}")
        total_rows = count_res['total'] if count_res else 0

        columns_meta = []
        foreign_keys_meta = []

        if self.db_type == 'sqlite':
            # PRAGMA table_info
            col_info = self.fetch_all(f"PRAGMA table_info({canonical_name});")
            for col in col_info:
                columns_meta.append({
                    "cid": col['cid'],
                    "name": col['name'],
                    "type": col['type'],
                    "notnull": bool(col['notnull']),
                    "dflt_value": col['dflt_value'],
                    "pk": bool(col['pk'])
                })
            
            # PRAGMA foreign_key_list
            fk_info = self.fetch_all(f"PRAGMA foreign_key_list({canonical_name});")
            for fk in fk_info:
                foreign_keys_meta.append({
                    "from": fk['from'],
                    "table": fk['table'],
                    "to": fk['to'],
                    "on_update": fk['on_update'],
                    "on_delete": fk['on_delete']
                })
        else:
            # Oracle column info
            col_query = """
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns
                WHERE UPPER(table_name) = UPPER(?)
                ORDER BY column_id
            """
            col_info = self.fetch_all(col_query, (canonical_name,))
            for col in col_info:
                columns_meta.append({
                    "name": col.get('COLUMN_NAME') or col.get('column_name'),
                    "type": col.get('DATA_TYPE') or col.get('data_type'),
                    "notnull": (col.get('NULLABLE') or col.get('nullable')) == 'N',
                    "pk": (col.get('COLUMN_NAME') or col.get('column_name')).upper().endswith('_ID')
                })

        return {
            "table_name": canonical_name,
            "total_records": total_rows,
            "columns": columns_meta,
            "foreign_keys": foreign_keys_meta
        }


# Global singleton instance
db = DatabaseManager()
