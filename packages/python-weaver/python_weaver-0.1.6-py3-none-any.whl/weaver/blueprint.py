"""
Blueprint: SQLite-backed task tracker for python-weaver.

Manages tasks with persistence, dependency resolution, CSV import/export, and state updates.
"""
import sqlite3
from sqlite3 import Connection, Cursor
from datetime import datetime
import pandas as pd
from .exceptions import DatabaseError, ValidationError


class Blueprint:
    """
    SQLite-backed task tracker.
    """
    # Columns in the tasks table
    _schema_columns = {
        'task_id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'task_name': 'TEXT NOT NULL',
        'status': "TEXT NOT NULL DEFAULT 'pending'",  # pending, awaiting_human_approval, in_progress, completed, failed, skipped
        'llm_config_key': 'TEXT NOT NULL',
        'prompt_template': 'TEXT',
        'final_prompt': 'TEXT',
        'raw_result': 'TEXT',
        'parsed_result': 'TEXT',
        'dependencies': 'TEXT',  # comma-separated task_ids
        'creation_timestamp': 'TEXT NOT NULL',  # ISO-8601 string
        'execution_start_timestamp': 'TEXT',
        'execution_end_timestamp': 'TEXT',
        'cost': 'REAL',
        'retry_count': 'INTEGER DEFAULT 0',
        'error_log': 'TEXT',
        'human_notes': 'TEXT'
    }

    def __init__(self, db_path: str):
        """
        Connects to (or creates) the SQLite database and ensures the tasks table exists.
        """
        try:
            self.conn: Connection = sqlite3.connect(db_path, check_same_thread=False)
            self._initialize_table()
        except Exception as e:
            raise DatabaseError(f"Failed to connect to SQLite DB at '{db_path}': {e}")


    
    def _initialize_table(self) -> None:
        """
        Create tasks table if not exists, according to the defined schema.
        """
        cols_defs = ",\n".join([
            f"{col} {typ}" for col, typ in self._schema_columns.items()
        ])
        create_sql = f"CREATE TABLE IF NOT EXISTS tasks (\n{cols_defs}\n);"
        self._execute_query(create_sql)
        self.conn.commit()

    def _execute_query(self, query: str, params: tuple = (), fetch: str = None):
        """
        Execute a SQL query with parameters. Optionally fetch results:
        - fetch='one' returns a single row
        - fetch='all' returns all rows
        - fetch=None returns cursor
        """
        try:
            cur: Cursor = self.conn.cursor()
            cur.execute(query, params)
            if fetch == 'one':
                return cur.fetchone()
            if fetch == 'all':
                return cur.fetchall()
            return cur
        except Exception as e:
            self.conn.rollback()
            raise DatabaseError(f"SQLite query failed: {e} -- Query: {query} -- Params: {params}")

    def add_task(
        self,
        task_name: str,
        llm_config_key: str,
        prompt_template: str,
        dependencies: str = None,
        human_notes: str = None
    ) -> int:
        """
        Add a new task. Returns the new task_id.
        """
        now = datetime.utcnow().isoformat()
        deps = dependencies or ''
        notes = human_notes or ''
        sql = (
            "INSERT INTO tasks (task_name, llm_config_key, prompt_template, "
            "dependencies, human_notes, creation_timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)"
        )
        cur = self._execute_query(sql, (task_name, llm_config_key, prompt_template, deps, notes, now))
        self.conn.commit()
        return cur.lastrowid

    def get_task(self, task_id: int) -> dict:
        """
        Fetch a single task by ID. Returns dict or None if not found.
        """
        sql = "SELECT * FROM tasks WHERE task_id = ?"
        row = self._execute_query(sql, (task_id,), fetch='one')
        if not row:
            return None
        cols = [info[1] for info in self._execute_query("PRAGMA table_info(tasks)", fetch='all')]
        return dict(zip(cols, row))

    def get_next_pending_task(self) -> dict:
        """
        Get the next 'pending' task whose dependencies are all 'completed'.
        Returns dict or None.
        """
        # Step 1: fetch all pending tasks
        pending = self._execute_query(
            "SELECT task_id, dependencies FROM tasks WHERE status = 'pending' ORDER BY creation_timestamp",
            fetch='all'
        )
        if not pending:
            return None
        # Step 2: iterate and check dependencies
        for task_id, deps_str in pending:
            if not deps_str:
                return self.get_task(task_id)
            dep_ids = [d.strip() for d in deps_str.split(',') if d.strip().isdigit()]
            if not dep_ids:
                return self.get_task(task_id)
            # count completed deps
            placeholders = ','.join('?' for _ in dep_ids)
            q = (
                f"SELECT COUNT(*) FROM tasks "
                f"WHERE task_id IN ({placeholders}) AND status = 'completed'"
            )
            count = self._execute_query(q, tuple(dep_ids), fetch='one')[0]
            if count == len(dep_ids):
                return self.get_task(task_id)
        return None

    def update_task_status(self, task_id: int, status: str) -> None:
        """
        Update the status of a task.
        """
        sql = "UPDATE tasks SET status = ? WHERE task_id = ?"
        self._execute_query(sql, (status, task_id))
        self.conn.commit()

    def update_task_execution_details(
        self,
        task_id,
        final_prompt=None,
        raw_result=None,
        parsed_result=None,
        cost=None,
        execution_start_timestamp=None,
        execution_end_timestamp=None,
        retry_count=None,
        error_log=None
    ):
        """
        Update any of these fields on a task. Only non-None args will be written.
        """
        updates = {}
        if final_prompt    is not None: updates['final_prompt']    = final_prompt
        if raw_result      is not None: updates['raw_result']      = raw_result
        if parsed_result   is not None: updates['parsed_result']   = parsed_result
        if cost             is not None: updates['cost']            = cost
        if execution_start_timestamp is not None:
            updates['execution_start_timestamp'] = execution_start_timestamp
        if execution_end_timestamp   is not None:
            updates['execution_end_timestamp']   = execution_end_timestamp
        if retry_count      is not None: updates['retry_count']      = retry_count
        if error_log        is not None: updates['error_log']        = error_log

        if not updates:
            return

        set_clause = ", ".join(f"{col} = ?" for col in updates)
        params     = list(updates.values()) + [task_id]
        sql = f"UPDATE tasks SET {set_clause} WHERE task_id = ?"
        self._execute_query(sql, params=params)

    def to_csv(self, filepath: str) -> None:
        """
        Export tasks table to CSV.
        """
        df = pd.read_sql_query("SELECT * FROM tasks", self.conn)
        df.to_csv(filepath, index=False)

    def import_from_csv(self, filepath: str) -> None:
        """
        Import CSV, validate schema, and apply updates transactionally.
        """
        df = pd.read_csv(filepath)
        required = {'task_id', 'task_name', 'status', 'llm_config_key', 'prompt_template'}
        missing = required - set(df.columns)
        if missing:
            raise ValidationError(f"CSV missing required columns: {missing}")
        self.update_from_df(df)

    def update_from_df(self, df: pd.DataFrame) -> None:
        """
        Transactionally update user-editable fields based on a DataFrame.
        Only updates: task_name, llm_config_key, prompt_template, dependencies, human_notes, status.
        Ignores new rows.
        """
        editable = [
            'task_name', 'llm_config_key', 'prompt_template',
            'dependencies', 'human_notes', 'status'
        ]
        # Fetch current state
        current = pd.read_sql_query("SELECT * FROM tasks", self.conn, index_col='task_id')
        incoming = df.set_index('task_id')
        updates = []  # list of (task_id, {col: new_val, ...})
        
        for tid, row in incoming.iterrows():
            if tid not in current.index:
                continue  # skip new tasks
            changes = {}
            for col in editable:
                if col in incoming.columns:
                    new_val = row[col]
                    old_val = current.at[tid, col]
                    
                    # Special handling for dependencies column
                    if col == 'dependencies' and pd.notna(new_val):
                        # Clean up dependencies: convert floats to ints
                        if isinstance(new_val, (int, float)):
                            new_val = str(int(new_val))
                        elif isinstance(new_val, str):
                            # Handle comma-separated dependencies
                            deps = []
                            for dep in new_val.split(','):
                                dep = dep.strip()
                                if dep:
                                    try:
                                        deps.append(str(int(float(dep))))
                                    except (ValueError, TypeError):
                                        print(f"[weaver] Warning: Invalid dependency '{dep}' in task {tid}")
                            new_val = ','.join(deps) if deps else ''
                    
                    if pd.notna(new_val) and new_val != old_val:
                        changes[col] = new_val
            if changes:
                updates.append((tid, changes))
                
        if not updates:
            return
            
        # Apply in a single transaction
        try:
            self._execute_query("BEGIN TRANSACTION")
            for tid, changes in updates:
                set_clause = ", ".join([f"{col} = ?" for col in changes])
                params = list(changes.values()) + [tid]
                sql = f"UPDATE tasks SET {set_clause} WHERE task_id = ?"
                self._execute_query(sql, tuple(params))
            self._execute_query("COMMIT")
            self.conn.commit()
        except Exception as e:
            self._execute_query("ROLLBACK")
            self.conn.commit()
            raise DatabaseError(f"Failed to update from DataFrame: {e}")