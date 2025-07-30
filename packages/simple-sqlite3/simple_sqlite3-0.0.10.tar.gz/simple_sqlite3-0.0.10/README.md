# Simple SQLite3
[![PyPI version](https://badge.fury.io/py/simple-sqlite3.svg)](https://pypi.org/project/simple-sqlite3/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
[![SQLite 3](https://img.shields.io/badge/SQLite_3.0+-003B57.svg?logo=sqlite&logoColor=white)](https://www.sqlite.org/index.html)

Effortless, Pythonic SQLite database management with a modern API and CLI.

**Simple SQLite3** is a lightweight, Pythonic wrapper for Python’s built-in `sqlite3` module, making it easy to work with SQLite databases. It offers a user-friendly API for managing tables, inserting and querying data, and exporting results, with built-in support for JSON/CSV/TXT, schema evolution, and a convenient CLI.

---

## Features

- Easy-to-use API for SQLite database and table management.
- Command-line interface (CLI) for database operations.
- Support for exporting data to JSON, CSV and TXT formats.
- Robust to both nested and non-nested data, with datetime support.
- Utilities for processing queried results.

---

## Installation

Requires **Python 3.9+**.

The package is available on [PyPI](https://pypi.org/project/simple-sqlite3/):

```bash
pip install simple-sqlite3
```

---

## Quick Start

### Programmatic Usage

#### 1. Insert and Query

This example demonstrates how to insert multiple rows into a table and query all records.

```python
from simple_sqlite3 import Database

db = Database("database.db")
table = db.table("people")

table.insert(
    [
        {"name": "Amy", "age": 30, "city": "Helsinki"},
        {"name": "Bob", "age": 25, "city": "Cambridge"},
        {"name": "Cat", "age": 20, "city": "Paris"},
    ]
)

results = table.query("SELECT *")

print(results)
```

**Example Output (from `print(results)`)**:
```python
[
    {"name": "Amy", "age": 30, "city": "Helsinki"},
    {"name": "Bob", "age": 25, "city": "Cambridge"},
    {"name": "Cat", "age": 20, "city": "Paris"},
]
```

#### 2. Bulk Insert Large Datasets

This example demonstrates how to efficiently insert many rows using either the `insert_fast` or `insert_many` methods. Both are designed for high performance with large datasets:

- **`insert_fast`**: Use when your data is a list of dictionaries, and all dictionaries have the same keys (homogeneous). This is ideal for bulk-inserting structured data with column names, and supports schema inference or explicit schema.
- **`insert_many`**: Use when your data is a list of tuples/lists (not dicts). This is fastest for simple, flat data and is less flexible (does not handle missing columns or nested data).

> **Note:** Both methods provide significant speed efficiencies for large datasets. Use `insert_fast` for homogeneous dicts, and `insert_many` for tuple/list rows.

**Example: Using `insert_fast` (homogeneous dicts)**

```python
from simple_sqlite3 import Database

db = Database(":memory:")
table = db.table("people")

data = [
    {"name": "Amy", "age": 30, "city": "Helsinki"},
    {"name": "Bob", "age": 25, "city": "Cambridge"},
    {"name": "Cat", "age": 20, "city": "Paris"},
]

table.insert_fast(data) # Or table.insert(data, fast=True)
```

**Example: Using `insert_many` (tuples/lists)**

```python
from simple_sqlite3 import Database

db = Database(":memory:")
table = db.table("people")

rows = [
    ("Amy", 30, "Helsinki"),
    ("Bob", 25, "Cambridge"),
    ("Cat", 20, "Paris"),
]
columns = ("name", "age", "city")
schema = "name TEXT, age INTEGER, city TEXT" # Optional

table.insert_many(rows, columns, schema=schema)
```

#### 3. Insert Nested Data

This example demonstrates inserting nested (dictionary) data, which is automatically stored as JSON in SQLite.

```python
from simple_sqlite3 import Database

db = Database("database.db")
table = db.table("nested")

table.insert(
    [
        {
            "country": "Finland",
            "info": {
                "capital": "Helsinki",
                "latitude": 60.1699,
                "longitude": 24.9384,
            },
        },
        {
            "country": "France",
            "info": {
                "capital": "Paris",
                "latitude": 48.8566,
                "longitude": 2.3522,
            },
        },
        {
            "country": "Japan",
            "info": {
                "capital": "Tokyo",
                "latitude": 35.6895,
                "longitude": 139.6917,
            },
        },
    ]
)
```

#### 4. Insert and Query Timeseries

This example demonstrates how to insert timeseries data using Python `datetime` objects and conditionally query rows, automatically parsing dates.

```python
from simple_sqlite3 import Database
from datetime import datetime as dt

db = Database("database.db")
table = db.table("timeseries")

table.insert(
    [
        {"date": dt(2024, 6, 1), "value": 1.2345, "pair": "EURUSD"},
        {"date": dt(2024, 6, 2), "value": 1.2350, "pair": "EURUSD"},
        {"date": dt(2024, 6, 3), "value": 1.2360, "pair": "EURUSD"},
        {"date": dt(2024, 6, 4), "value": 1.2375, "pair": "EURUSD"},
        {"date": dt(2024, 6, 1), "value": 109.45, "pair": "USDJPY"},
        {"date": dt(2024, 6, 2), "value": 109.60, "pair": "USDJPY"},
        {"date": dt(2024, 6, 3), "value": 109.75, "pair": "USDJPY"},
        {"date": dt(2024, 6, 4), "value": 109.90, "pair": "USDJPY"},
    ]
)

results = table.query("SELECT date, value WHERE pair = 'EURUSD'", auto_parse_dates=True)

print(results)
```

**Example Output (from `print(results)`)**:
```python
[
    {"date": datetime.datetime(2024, 6, 1, 0, 0), "value": 1.2345},
    {"date": datetime.datetime(2024, 6, 2, 0, 0), "value": 1.235},
    {"date": datetime.datetime(2024, 6, 3, 0, 0), "value": 1.236},
    {"date": datetime.datetime(2024, 6, 4, 0, 0), "value": 1.2375},
]
```

#### 5. Insert Mixed Data

This example demonstrates inserting mixed data, including deeply-nested dictionaries.

```python
from simple_sqlite3 import Database
from datetime import datetime as dt

db = Database("database.db")
table = db.table("mixed_data")

table.insert(
    [
        {
            "date": dt(2024, 6, 1),
            "value": 1.2345,
            "pair": "EURUSD",
            "source": "ECB",
        },
        {
            "date": dt(2024, 6, 1),
            "value": 109.45,
            "pair": "USDJPY",
            "source": "BOJ",
        },
        {
            "date": dt(2024, 6, 2),
            "value": 0.8567,
            "pair": "EURGBP",
            "source": "ECB",
        },
        {
            "date": dt(2024, 6, 2),
            "value": 1.4200,
            "pair": "GBPUSD",
            "source": "FED",
        },
        {
            "date": dt(2024, 6, 2),
            "value": 1.2370,
            "pair": "EURUSD",
            "source": "ECB",
            "meta": {
                "confidence": 0.98,
                "contributors": ["ECB", "Bloomberg"],
                "valuation": {"buy": 0.4, "hold": 0.2, "sell": 0.4},
            },
        },
        {
            "date": dt(2024, 6, 3),
            "value": 109.80,
            "pair": "USDJPY",
            "source": "BOJ",
            "meta": {"confidence": 0.95, "contributors": ["BOJ"]},
        },
    ]
)
```

#### 6. Insert Data Into Memory and Export as JSON, CSV and TXT

This example demonstrates inserting data into an in-memory database and exporting the table to JSON, CSV, and TXT formats.

```python
from simple_sqlite3 import Database
from datetime import datetime as dt

db = Database(":memory:")
table = db.table("timeseries")

table.insert(
    [
        {"date": dt(2025, 5, 22), "value": 5328, "idx": "S&P 500"},
        {"date": dt(2025, 5, 21), "value": 5421, "idx": "S&P 500"},
        {"date": dt(2025, 5, 22), "value": 5448, "idx": "EURO STOXX 50"},
        {"date": dt(2025, 5, 21), "value": 5452, "idx": "EURO STOXX 50"},
    ]
)

table.export_to_json("timeseries.json")
table.export_to_csv("timeseries.csv")
table.export_to_txt("timeseries.txt")
```

#### 7. Exporting Queried Results

This example demonstrates how to export queried results using the `QueryResultsProcessor` utility.

```python
from simple_sqlite3 import Database
from simple_sqlite3.utils import QueryResultsProcessor
from datetime import datetime as dt

db = Database(":memory:")
table = db.table("timeseries")

table.insert(
    [
        {"date": dt(2025, 5, 22), "value": 5328, "idx": "S&P 500"},
        {"date": dt(2025, 5, 21), "value": 5421, "idx": "S&P 500"},
        {"date": dt(2025, 5, 22), "value": 5448, "idx": "EURO STOXX 50"},
        {"date": dt(2025, 5, 21), "value": 5452, "idx": "EURO STOXX 50"},
    ]
)

results = table.query("SELECT * WHERE idx = 'EURO STOXX 50'")

processor = QueryResultsProcessor(results)

processor.to_json("timeseries.json")
processor.to_csv("timeseries.csv")
processor.to_txt("timeseries.txt")
```

#### 8. Grouping Queried Data

This example demonstrates how to group queried data into a matrix format for easy analysis.

```python
from simple_sqlite3 import Database
from simple_sqlite3.utils import QueryResultsProcessor
from datetime import datetime as dt

db = Database(":memory:")
table = db.table("timeseries")

table.insert(
    [
        {"date": dt(2024, 6, 1), "value": 1.2345, "pair": "EURUSD"},
        {"date": dt(2024, 6, 2), "value": 1.2350, "pair": "EURUSD"},
        {"date": dt(2024, 6, 3), "value": 1.2360, "pair": "EURUSD"},
        {"date": dt(2024, 6, 4), "value": 1.2375, "pair": "EURUSD"},
        {"date": dt(2024, 6, 1), "value": 109.45, "pair": "USDJPY"},
        {"date": dt(2024, 6, 2), "value": 109.60, "pair": "USDJPY"},
        {"date": dt(2024, 6, 3), "value": 109.75, "pair": "USDJPY"},
        {"date": dt(2024, 6, 4), "value": 109.90, "pair": "USDJPY"},
    ]
)

results = table.query("SELECT *", auto_parse_dates=True)

processor = QueryResultsProcessor(results)

results_matrix_format = processor.to_matrix_format(
    index_key="date", group_key="pair", value_key="value"
)

print(results_matrix_format)
```

**Example Output (from `print(results)`)**:
```python
{
    "index": [
        datetime.datetime(2024, 6, 1, 0, 0),
        datetime.datetime(2024, 6, 2, 0, 0),
        datetime.datetime(2024, 6, 3, 0, 0),
        datetime.datetime(2024, 6, 4, 0, 0),
    ],
    "columns": ["EURUSD", "USDJPY"],
    "values": [[1.2345, 109.45], [1.235, 109.6], [1.236, 109.75], [1.2375, 109.9]],
}
```

#### 9. Querying Directly From a Database

This example demonstrates querying directly from a pre-existing database called `database.db` with a table called `timeseries` using context manager.

```python
from simple_sqlite3 import Database

with Database("database.db") as db:
    results = db.query("SELECT * FROM timeseries")

...
```

---

### CLI Usage

The CLI is installed automatically with the package:

```bash
pip install simple-sqlite3
```

You can run the CLI using the `db` command (if your Python scripts directory is in your PATH or you have an active virtual environment), or with:

```bash
python -m simple_sqlite3.cli
```

#### CLI Command Overview

| Command              | Description                                                      |
|----------------------|------------------------------------------------------------------|
| `db --help`          | Show help and available commands                                 |
| `query`              | Query records from a table                                       |
| `insert`             | Insert data from a file (CSV, JSON, TXT)                         |
| `export`             | Export table data to a file (CSV, JSON, TXT)                     |
| `rename-column`      | Rename a column in a table                                       |
| `rename-columns`     | Rename multiple columns in a table                               |
| `delete-column`      | Delete a column from a table                                     |
| `delete-columns`     | Delete multiple columns from a table                             |
| `rename-table`       | Rename a table                                                   |
| `delete-duplicates`  | Remove duplicate rows from a table                               |
| `delete-table`       | Delete a table from the database                                 |
| `delete-database`    | Delete the entire database file                                  |
| `vacuum`             | Reclaim unused space and optimize the database file              |

#### Common Flags

| Short | Long         | Description                                 |
|-------|--------------|---------------------------------------------|
| `-d`  | `--database` | Path to the SQLite database                 |
| `-t`  | `--table`    | Name of the table                           |
| `-f`  | `--file`     | Input/output file path                      |
| `-s`  | `--sql`      | SQL query to execute                        |
| `-F`  | `--force`    | Force action without confirmation           |

---

#### Show CLI help

Displays help and available commands.

```bash
db --help
```

#### Insert data from a JSON file into a table

Inserts data from `timeseries.json` into the `timeseries` table in `database.db`.

```bash
db insert -d database.db -t timeseries -f timeseries.json
```

If you don't have a `timeseries.json` file, you can create one with the following example content:

```json
[
    {"date": "2025-05-22", "value": 5328, "idx": "S&P 500"},
    {"date": "2025-05-21", "value": 5421, "idx": "S&P 500"},
    {"date": "2025-05-22", "value": 5448, "idx": "EURO STOXX 50"},
    {"date": "2025-05-21", "value": 5452, "idx": "EURO STOXX 50"}
]
```

#### Query all rows from a table

Queries all rows from the `timeseries` table.

```bash
db query -d database.db -t timeseries -s "SELECT *"
```

#### Query database and save results to JSON format

Queries specific rows and saves results as `results.json`.

```bash
db query -d database.db -s "SELECT * FROM timeseries WHERE idx = 'EURO STOXX 50'" -f results.json
```

#### Remove duplicate rows from a table

Removes duplicate rows from the `timeseries` table.

```bash
db delete-duplicates -d database.db -t timeseries
```

#### Export a table to CSV format

Exports the `timeseries` table to `timeseries.csv`.

```bash
db export -d database.db -t timeseries -f timeseries.csv
```

#### Delete a table from the database

Deletes the `timeseries` table from `database.db`. Use `-F` to skip confirmation.

```bash
db delete-table -d database.db -t timeseries -F
```

#### Delete the entire database file

Deletes the `database.db` file. Use `-F` to skip confirmation.

```bash
db delete-database -d database.db -F
```

---

## Advanced Features

- **Automatic WAL Mode:** Write-Ahead Logging for better concurrency (default).
- **Schema Evolution:** New columns are added automatically on insert if `force=True` (default).
- **Batch Export:** Efficiently export large tables in batches to avoid memory issues.

---

## License

This project is developed by Rob Suomi and licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.