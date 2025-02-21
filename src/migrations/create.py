import sqlite3
from pathlib import Path

script_dir = Path(__file__).parent.parent
database_file = script_dir / "db/main.db"

conn = sqlite3.connect(database_file)

cursor = conn.cursor()

sql_tables = {
    "USER": """CREATE TABLE User(
        user_id CHAR(20) NOT NULL,
        username CHAR(50) NOT NULL,
        join_date TIMESTAMP NOT NULL
    )""",
    "USER_STOCK": """CREATE TABLE USER_STOCK(
        user_id CHAR(20) NOT NULL,
        stock_url VARCHAR(255) NOT NULL,
        stock_name VARCHAR(50) NOT NULL,
        stock_status INTEGER NOT NULL, /*Stock_Status enum, 0 oos, 1 in stock*/
        date_added TIMESTAMP NOT NULL,
        last_checked TIMESTAMP NOT NULL,
        check_interval INTEGER NOT NULL, /*Seconds*/
        price VARCHAR(50) NOT NULL
    )""",
}

for key in sql_tables:
    _ = cursor.execute(sql_tables[key])
    print(f"Created table {key}")

conn.commit()
print("Changes committed")

conn.close()
print("Connection to db closed")
