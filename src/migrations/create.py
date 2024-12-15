import sqlite3
from pathlib import Path

script_dir = Path(__file__).parent.parent
database_file = script_dir / "db/main.db"

conn = sqlite3.connect(database_file)

cursor = conn.cursor()

sql_tables = {
    "USER": """CREATE TABLE User(
        user_id CHAR(20) NOT NULL,
        username CHAR(50) NOT NULL
    )""",
    "USER_STOCK": """CREATE TABLE USER_STOCK(
        user_id CHAR(20) NOT NULL,
        stock_url VARCHAR(255) NOT NULL,
        stock_name VARCHAR(50) NOT NULL 
    )""",
}

for key in sql_tables:
    _ = cursor.execute(f"DROP TABLE IF EXISTS {key}")
    print(f"Dropped table {key}")

for key in sql_tables:
    _ = cursor.execute(sql_tables[key])
    print(f"Created table {key}")

# cursor.execute(sql_create_tables)
print("Tables created")

conn.commit()
print("Changes committed")

conn.close()
