import csv
import json
import argparse
import sqlite3
import os
from .table import Table, validate_cli_identifier
from .database import Database
from .utils import QueryResultsProcessor
from typing import Optional


def prompt_confirm(message: str) -> bool:
    """Prompt the user for confirmation. Returns True if confirmed."""
    reply = input(f"{message} [y/N]: ").strip().lower()
    return reply == "y" or reply == "yes"


def main():
    parser = argparse.ArgumentParser(
        description="Command-line interface for SQLite database manipulation."
    )

    subparsers = parser.add_subparsers(
        dest="action", required=True, help="Database actions"
    )

    # Subparser for inserting data
    insert_parser = subparsers.add_parser(
        "insert",
        help="Insert data into a table from a file. All CSV/TXT values are imported as strings for safety; change types later if needed.",
    )
    insert_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    insert_parser.add_argument("-t", "--table", required=True, help="Name of the table")
    insert_parser.add_argument(
        "-f", "--file", required=True, help="Input file path (.json, .csv or .txt)"
    )

    # Subparser for querying records
    query_parser = subparsers.add_parser(
        "query",
        help="Query records from a table or run a raw SQL query if no table is specified",
    )
    query_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    query_parser.add_argument(
        "-t", "--table", required=False, help="Name of the table (optional)"
    )
    query_parser.add_argument("-s", "--sql", required=True, help="SQL query to execute")
    query_parser.add_argument(
        "-f", "--file", help="Output file path (.json, .csv or .txt [optional])"
    )

    # Subparser for deleting a database
    delete_database_parser = subparsers.add_parser(
        "delete-database", help="Delete a database"
    )
    delete_database_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    delete_database_parser.add_argument(
        "-F", "--force", action="store_true", help="Force deletion without confirmation"
    )

    # Subparser for deleting a table
    delete_table_parser = subparsers.add_parser(
        "delete-table",
        help="Delete a specific table from a database, optionally by name or flag",
    )
    delete_table_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    delete_table_parser.add_argument(
        "table_positional", nargs="?", help="Name of the table to delete (positional)"
    )
    delete_table_parser.add_argument(
        "-t", "--table", help="Name of the table to delete (optional flag)"
    )
    delete_table_parser.add_argument(
        "-F", "--force", action="store_true", help="Force deletion without confirmation"
    )

    # Subparser for renaming a column
    rename_column_parser = subparsers.add_parser(
        "rename-column", help="Rename a column in a table"
    )
    rename_column_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    rename_column_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    rename_column_parser.add_argument("old_name", help="Current name of the column")
    rename_column_parser.add_argument("new_name", help="New name for the column")
    rename_column_parser.add_argument(
        "-F", "--force", action="store_true", help="Force renaming without confirmation"
    )

    # Subparser for deleting a column
    delete_column_parser = subparsers.add_parser(
        "delete-column", help="Delete a column from a table"
    )
    delete_column_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    delete_column_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    delete_column_parser.add_argument("column", help="Name of the column to delete")
    delete_column_parser.add_argument(
        "-F", "--force", action="store_true", help="Force deletion without confirmation"
    )

    # Subparser for renaming multiple columns
    rename_columns_parser = subparsers.add_parser(
        "rename-columns", help="Rename multiple columns in a table"
    )
    rename_columns_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    rename_columns_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    rename_columns_parser.add_argument(
        "columns", nargs="+", help="Pairs of old and new column names"
    )
    rename_columns_parser.add_argument(
        "-F", "--force", action="store_true", help="Force renaming without confirmation"
    )

    # Subparser for deleting multiple columns
    delete_columns_parser = subparsers.add_parser(
        "delete-columns", help="Delete multiple columns from a table"
    )
    delete_columns_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    delete_columns_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    delete_columns_parser.add_argument(
        "columns", nargs="+", help="Names of columns to delete"
    )
    delete_columns_parser.add_argument(
        "-F", "--force", action="store_true", help="Force deletion without confirmation"
    )

    # Subparser for renaming a table
    rename_table_parser = subparsers.add_parser("rename-table", help="Rename a table")
    rename_table_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    rename_table_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    rename_table_parser.add_argument("new_name", help="New name for the table")
    rename_table_parser.add_argument(
        "-F", "--force", action="store_true", help="Force renaming without confirmation"
    )

    # Subparser for dropping duplicates
    delete_duplicates_parser = subparsers.add_parser(
        "delete-duplicates", help="Drop duplicate rows from a table"
    )
    delete_duplicates_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    delete_duplicates_parser.add_argument(
        "-t", "--table", required=True, help="Name of the table"
    )
    delete_duplicates_parser.add_argument(
        "--columns", nargs="+", help="Columns to check for duplicates (optional)"
    )
    delete_duplicates_parser.add_argument(
        "--keep",
        choices=["first", "last"],
        default="last",
        help="Which duplicate to keep: 'last' (default) or 'first'",
    )

    # Subparser for exporting data
    export_parser = subparsers.add_parser("export", help="Export table data to a file")
    export_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )
    export_parser.add_argument("-t", "--table", required=True, help="Name of the table")
    export_parser.add_argument("-f", "--file", required=True, help="Output file path")

    # Subparser for vacuuming the database
    vacuum_parser = subparsers.add_parser(
        "vacuum", help="Run VACUUM to optimize the database"
    )
    vacuum_parser.add_argument(
        "-d", "--database", required=True, help="Path to the SQLite database"
    )

    args = parser.parse_args()

    if args.action == "query":
        ext = os.path.splitext(args.file)[1].lower() if args.file else None
        if ext == ".csv":
            output_format = "csv"
        elif ext == ".json":
            output_format = "json"
        elif ext == ".txt":
            output_format = "txt"
        else:
            output_format = None
            if args.file:
                print(
                    "Could not detect format from file extension. Please use .csv, .json, or .txt."
                )
                return
        query_records(args.database, args.table, args.sql, args.file, output_format)
    elif args.action == "delete-database":
        delete_database(args.database, args.force)
    elif args.action == "delete-table":
        # Prefer the flag, fall back to positional
        table_name = args.table or args.table_positional
        if not table_name:
            print(
                "Error: Table name must be specified as a positional argument or with -t/--table."
            )
            return
        delete_table(args.database, table_name, args.force)
    elif args.action == "rename-column":
        rename_column(
            args.database, args.table, args.old_name, args.new_name, args.force
        )
    elif args.action == "delete-column":
        delete_column(args.database, args.table, args.column, args.force)
    elif args.action == "rename-columns":
        rename_columns(args.database, args.table, args.columns, args.force)
    elif args.action == "delete-columns":
        delete_columns(args.database, args.table, args.columns, args.force)
    elif args.action == "rename-table":
        rename_table(args.database, args.table, args.new_name, args.force)
    elif args.action == "delete-duplicates":
        delete_duplicates(args.database, args.table, args.columns, args.keep)
    elif args.action == "export":
        ext = os.path.splitext(args.file)[1].lower()
        if ext == ".csv":
            export_format = "csv"
        elif ext == ".json":
            export_format = "json"
        elif ext == ".txt":
            export_format = "txt"
        else:
            print(
                "Could not detect format from file extension. Please use .csv, .json, or .txt."
            )
            return
        export_table(args.database, args.table, export_format, args.file)
    elif args.action == "insert":
        ext = os.path.splitext(args.file)[1].lower()
        if ext == ".csv":
            insert_format = "csv"
        elif ext == ".json":
            insert_format = "json"
        elif ext == ".txt":
            insert_format = "txt"
        else:
            print(
                "Could not detect format from file extension. Please use .csv, .json, or .txt."
            )
            return
        insert_into_table(args.database, args.table, insert_format, args.file)
    elif args.action == "vacuum":
        vacuum_database(args.database)
    else:
        parser.print_help()


def query_records(
    database_path: str,
    table_name: Optional[str],
    sql: str,
    file: Optional[str] = None,
    file_format: Optional[str] = None,
) -> None:
    """
    Queries records from a table and optionally exports the results to a file using Table's export methods. These supports CSV, JSON, and TXT (tab-delimited) formats.
    If no file is specified, results are printed in JSON format.
    """
    if not os.path.exists(database_path):
        print(f"Database file '{database_path}' does not exist.")
        return
    with Database(database_path) as db:
        if table_name:
            table = Table(db.connection, table_name)
            results = table.query(sql)
        else:
            results = db.query(sql)

        processor = QueryResultsProcessor(results)

        if file:
            if file_format == "csv":
                processor.to_csv(file)
            elif file_format == "json":
                processor.to_json(file)
            elif file_format == "txt":
                processor.to_txt(file)
            else:
                print(f"Unsupported export format: {file_format}")
        else:
            # Attempt to decode JSON strings in results
            for row in results:
                for k, v in row.items():
                    if isinstance(v, str):
                        try:
                            if (v.startswith("{") and v.endswith("}")) or (
                                v.startswith("[") and v.endswith("]")
                            ):
                                row[k] = json.loads(v)
                        except Exception:
                            pass
            if results:
                formatted_results = json.dumps(results, indent=4, ensure_ascii=False)
                print(formatted_results)
            else:
                print("No results found.")


def insert_into_table(
    database_path: str,
    table_name: str,
    insert_format: str,
    input_path: str,
    batch_size: int = 1000,
):
    """
    Inserts data into a table from a file.
    Batch size can be specified to control how many records are inserted at once.

    Supported formats:
    - CSV: Expects a header row. All values are imported as strings to avoid accidental misinterpretation (e.g., '007' stays as '007').
    - TXT: Tab-delimited, expects a header row. All values are imported as strings.
    - JSON: Expects a list of dictionaries. Types are preserved as in the JSON file.

    Rationale:
    - By default, all CSV/TXT data are treated as string (default read) to ensure data safety and avoid issues with ambiguous values (e.g., codes, IDs, or dates that look like numbers).
    - Users can change column types later using SQL (e.g., ALTER TABLE) if needed.
    - This approach ensures flexibility and predictability for users.
    """
    table_name = validate_cli_identifier(table_name)
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        if insert_format == "csv":
            with open(input_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                # Strip whitespace and quotes from fieldnames
                reader.fieldnames = [
                    validate_cli_identifier(field.strip().strip('"').strip("'"))
                    for field in reader.fieldnames
                ]
                batch = []
                for row in reader:
                    clean_row = {
                        k: v.strip().strip('"').strip("'") if isinstance(v, str) else v
                        for k, v in row.items()
                    }
                    batch.append(clean_row)
                    if len(batch) >= batch_size:
                        table.insert(batch, fast=True)
                        batch = []
                if batch:
                    table.insert(batch, fast=True)
        elif insert_format == "txt":
            with open(input_path, "r", encoding="utf-8") as file:
                lines = file.read().splitlines()
                if not lines:
                    print("TXT file is empty.")
                    return
                header = lines[0].split("\t")
                batch = []
                for row in lines[1:]:
                    batch.append(dict(zip(header, row.split("\t"))))
                    if len(batch) >= batch_size:
                        table.insert(batch, fast=True)
                        batch = []
                if batch:
                    table.insert(batch, fast=True)
        elif insert_format == "json":
            with open(input_path, "r", encoding="utf-8") as file:
                records = json.load(file)
            if not records:
                print("No records to insert.")
                return
            table.insert(
                records
            )  # More flexible, can handle nested data (i.e. no fast=True)
        else:
            print("Unsupported file format.")
            return

        print(f"Data from '{input_path}' inserted into table '{table_name}'.")


def delete_database(database_path: str, force: bool = False):
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to delete the database '{database_path}'? This action cannot be undone."
        ):
            print("Aborted.")
            return
    if os.path.exists(database_path):
        # Check if file is a valid SQLite database
        try:
            with open(database_path, "rb") as f:
                header = f.read(16)
            if header != b"SQLite format 3\x00":
                print(
                    f"'{database_path}' does not appear to be a valid SQLite database (missing SQLite header). Aborted."
                )
                return
        except Exception as e:
            print(f"Could not read file '{database_path}': {e}")
            return
        os.remove(database_path)
        print(f"Database '{database_path}' deleted.")
    else:
        print(f"Database '{database_path}' does not exist.")


def delete_table(database_path: str, table_name: str, force: bool = False):
    table_name = validate_cli_identifier(table_name)
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to delete the table '{table_name}'? This action cannot be undone."
        ):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.commit()
        print(f"Table '{table_name}' deleted from database.")


def rename_column(
    database_path: str,
    table_name: str,
    old_name: str,
    new_name: str,
    force: bool = False,
):
    table_name = validate_cli_identifier(table_name)
    old_name = validate_cli_identifier(old_name)
    new_name = validate_cli_identifier(new_name)
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to rename column '{old_name}' to '{new_name}' in table '{table_name}'?"
        ):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.rename_column(old_name, new_name)
        print(f"Column '{old_name}' renamed to '{new_name}' in table '{table_name}'.")


def delete_column(
    database_path: str, table_name: str, column: str, force: bool = False
):
    table_name = validate_cli_identifier(table_name)
    column = validate_cli_identifier(column)
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to delete the column '{column}' from table '{table_name}'? This action cannot be undone."
        ):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.drop_columns(column)
        print(f"Column '{column}' deleted from table '{table_name}'.")


def rename_columns(
    database_path: str, table_name: str, columns: list[str], force: bool = False
):
    """
    Rename multiple columns in a table.
    columns: list of old/new name pairs, e.g. ['old1', 'new1', 'old2', 'new2']
    """
    if len(columns) % 2 != 0:
        print("Error: You must provide pairs of old and new column names.")
        return
    pairs = list(zip(columns[::2], columns[1::2]))
    table_name = validate_cli_identifier(table_name)
    if not force:
        msg = "Are you sure you want to rename the following columns in table '{}':\n".format(
            table_name
        )
        msg += "\n".join([f"  '{old}' -> '{new}'" for old, new in pairs])
        if not prompt_confirm(msg):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        for old, new in pairs:
            old = validate_cli_identifier(old)
            new = validate_cli_identifier(new)
            table.rename_column(old, new)
            print(f"Column '{old}' renamed to '{new}' in table '{table_name}'.")


def delete_columns(
    database_path: str, table_name: str, columns: list[str], force: bool = False
):
    """
    Delete multiple columns from a table.
    columns: list of column names to delete
    """
    table_name = validate_cli_identifier(table_name)
    columns = [validate_cli_identifier(col) for col in columns]
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to delete columns {columns} from table '{table_name}'? This action cannot be undone."
        ):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.drop_columns(*columns)
        print(f"Columns {columns} deleted from table '{table_name}'.")


def rename_table(
    database_path: str, table_name: str, new_name: str, force: bool = False
):
    table_name = validate_cli_identifier(table_name)
    new_name = validate_cli_identifier(new_name)
    if not force:
        if not prompt_confirm(
            f"Are you sure you want to rename table '{table_name}' to '{new_name}'?"
        ):
            print("Aborted.")
            return
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.rename(new_name)
        print(f"Table '{table_name}' renamed to '{new_name}'.")


def delete_duplicates(
    database_path: str, table_name: str, by: Optional[list[str]], keep: str = "last"
):
    table_name = validate_cli_identifier(table_name)
    if by:
        by = [validate_cli_identifier(col) for col in by]
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        table.delete_duplicates(by, keep=keep)
        print(
            f"Duplicates dropped from table '{table_name}' based on columns: {by}, keeping: {keep}."
        )


def export_table(
    database_path: str, table_name: str, export_format: str, output_path: str
):
    table_name = validate_cli_identifier(table_name)
    with sqlite3.connect(database_path) as conn:
        table = Table(conn, table_name)
        if export_format == "csv":
            table.export_to_csv(output_path)
        elif export_format == "json":
            table.export_to_json(output_path)
        elif export_format == "txt":
            table.export_to_txt(output_path)
        print(
            f"Table '{table_name}' exported to {export_format.upper()} at '{output_path}'."
        )


def vacuum_database(database_path: str):
    """Run VACUUM on the specified database."""
    with sqlite3.connect(database_path) as conn:
        conn.execute("VACUUM")
        print(f"Database '{database_path}' vacuumed (optimized).")


if __name__ == "__main__":
    main()
