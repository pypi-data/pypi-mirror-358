import sqlite3
import os
import json
import re
from datetime import datetime
from .table import Table


def _parse_dates_recursive(obj):
    if isinstance(obj, dict):
        return {k: _parse_dates_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_parse_dates_recursive(v) for v in obj]
    elif isinstance(obj, str):
        try:
            return datetime.fromisoformat(obj)
        except ValueError:
            return obj
    else:
        return obj


class Database:
    """Represents a SQLite database connection."""

    def __init__(self, path: str) -> None:
        """
        Initializes the database connection.

        Args:
            path (str): Path to the SQLite database file.

        Example:
        # In memory
        db = Database(":memory:")

        # On disk
        db = Database("my_database.db")
        """
        self.path = path
        self.connection = sqlite3.connect(path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def table(self, name: str) -> Table:
        """
        Returns a Table object for interacting with a specific table.

        Args:
            name (str): Name of the table.

        Returns:
            Table: A Table object for interacting with the specified table.
        """
        return Table(self.connection, name)

    def vacuum(self) -> None:
        """Optimizes the database by running the VACUUM command."""
        self.connection.execute("VACUUM")

    def close(self) -> None:
        """Closes the database connection."""
        self.connection.close()

    def connect(self) -> None:
        """Reconnects to the database."""
        self.connection = sqlite3.connect(self.path)

    def reset(self, confirm: bool = False) -> None:
        """
        Resets the database by deleting all tables and data.

        Args:
            confirm (bool): If True, skips confirmation prompt.
        """
        if not confirm:
            raise ValueError("Confirmation required to reset the database.")

        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
        self.connection.commit()

    def delete(self, confirm: bool = False) -> None:
        """
        Deletes the database file.

        Args:
            confirm (bool): If True, skips confirmation prompt.
        """
        if not confirm:
            raise ValueError("Confirmation required to delete the database file.")

        self.close()
        if os.path.exists(self.path):
            os.remove(self.path)
        else:
            raise FileNotFoundError("Database file does not exist.")

    def execute_sql(self, sql: str) -> None:
        """
        Executes a raw SQL command.

        Args:
            sql (str): The SQL command to execute.
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        self.connection.commit()

    def query(
        self, query: str, params: tuple = None, auto_parse_dates: bool = False
    ) -> list[dict]:
        """
        Executes a query on the database and returns the results as a list of dictionaries.
        Args:
            query (str): The SQL query to execute. Must start with SELECT or WITH.
            params (tuple, optional): Optional parameters for the query.
            auto_parse_dates (bool): If True, attempts to parse date strings into datetime objects.
        Returns:
            list[dict]: A list of dictionaries representing the query results.
        Raises:
            ValueError: If the query does not start with SELECT or WITH, or contains semicolons.
        """
        stripped = query.strip()
        upper = stripped.upper()
        if not (upper.startswith("SELECT") or upper.startswith("WITH")):
            raise ValueError("Only SELECT queries are allowed for safety.")
        if ";" in stripped:
            raise ValueError("Semicolons are not allowed in queries.")

        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]
        if auto_parse_dates:
            for row in results:
                for col, val in row.items():
                    # Try to decode JSON fields
                    if isinstance(val, str):
                        try:
                            if (val.startswith("{") and val.endswith("}")) or (
                                val.startswith("[") and val.endswith("]")
                            ):
                                val = json.loads(val)
                        except Exception:
                            pass
                    row[col] = _parse_dates_recursive(val)
        return results
