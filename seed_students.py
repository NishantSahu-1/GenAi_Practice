import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

DB_HOST = os.getenv("MYSQL_HOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = int(os.getenv("MYSQL_PORT", os.getenv("DB_PORT", 3306)))
DB_USER = os.getenv("MYSQL_USER", os.getenv("DB_USER"))
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", os.getenv("DB_PASSWORD"))
DB_NAME = os.getenv("MYSQL_DATABASE", os.getenv("DB_NAME"))

if not DB_USER or not DB_PASSWORD or not DB_NAME:
    raise ValueError("Missing MySQL credentials in .env or environment variables.")

connection = mysql.connector.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
)

first_names = [
    "Aarav", "Sara", "Rohan", "Priya", "Neha", "Arjun", "Mira", "Kiran",
    "Aditi", "Vikas", "Rhea", "Sameer", "Anika", "Jay", "Isha", "Rahul",
    "Tanya", "Kunal", "Zara", "Anil"
]
last_names = [
    "Shah", "Patel", "Singh", "Kumar", "Joshi", "Mehta", "Reddy", "Gandhi",
    "Desai", "Sharma", "Kapoor", "Iyer", "Nair", "Khan", "Ahuja"
]
cities = ["Mumbai", "Delhi", "Pune", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow"]
genders = ["Male", "Female", "Other"]
sections = ["A", "B", "C", "D"]
streams = ["Science", "Commerce", "Arts"]

TOTAL_ROWS = 5000
BATCH_SIZE = 1000

ALTER_COLUMNS = [
    ("email", "VARCHAR(255)"),
    ("phone", "VARCHAR(20)"),
    ("section", "VARCHAR(20)"),
    ("stream", "VARCHAR(50)"),
]


def generate_email(name: str) -> str:
    return f"{name.lower().replace(' ', '.')}.example@example.com"


def generate_phone() -> str:
    return f"9{random.randint(100000000, 999999999)}"


def generate_section(index: int) -> str:
    return sections[index % len(sections)]


def generate_stream(index: int) -> str:
    return streams[index % len(streams)]


with connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(255) NOT NULL,
                gender VARCHAR(20),
                city VARCHAR(100),
                age INT,
                marks INT,
                birthdate DATE,
                email VARCHAR(255),
                phone VARCHAR(20),
                section VARCHAR(20),
                stream VARCHAR(50)
            )
            """
        )

        for column_name, column_type in ALTER_COLUMNS:
            cursor.execute(
                "SHOW COLUMNS FROM students LIKE %s",
                (column_name,)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    f"ALTER TABLE students ADD COLUMN {column_name} {column_type}"
                )
                print(f"Added missing column: {column_name}")

        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]

        if count == 0:
            rows_to_insert = TOTAL_ROWS
            print(f"Inserting initial {rows_to_insert} rows into students table...")
            base_records = []
            start_birthdate = date(2004, 1, 1)
            for index in range(25):
                first = first_names[index % len(first_names)]
                last = last_names[index % len(last_names)]
                name = f"{first} {last}"
                gender = genders[index % len(genders)]
                city = cities[index % len(cities)]
                age = 16 + (index % 7)
                marks = 40 + (index * 3) % 61
                birthdate = start_birthdate + timedelta(days=(index * 45) % 1460)
                email = generate_email(name)
                phone = generate_phone()
                section = generate_section(index)
                stream = generate_stream(index)
                base_records.append((name, gender, city, age, marks, birthdate, email, phone, section, stream))

            sample_data = []
            for i in range(rows_to_insert):
                sample_data.append(base_records[i % len(base_records)])
                if len(sample_data) >= BATCH_SIZE:
                    cursor.executemany(
                        "INSERT INTO students (name, gender, city, age, marks, birthdate, email, phone, section, stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        sample_data,
                    )
                    connection.commit()
                    sample_data = []

            if sample_data:
                cursor.executemany(
                    "INSERT INTO students (name, gender, city, age, marks, birthdate, email, phone, section, stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    sample_data,
                )
                connection.commit()

        else:
            print(f"students table has {count} rows. Filling null values and duplicating rows if needed.")

            cursor.execute(
                "SELECT id, name, email, phone, section, stream FROM students WHERE email IS NULL OR phone IS NULL OR section IS NULL OR stream IS NULL"
            )
            null_rows = cursor.fetchall()
            if null_rows:
                updates = []
                for idx, name, email, phone, section, stream in null_rows:
                    first = name.split()[0] if name else "student"
                    generated_email = email or generate_email(name)
                    generated_phone = phone or generate_phone()
                    generated_section = section or generate_section(idx)
                    generated_stream = stream or generate_stream(idx)
                    updates.append((generated_email, generated_phone, generated_section, generated_stream, idx))

                cursor.executemany(
                    "UPDATE students SET email = %s, phone = %s, section = %s, stream = %s WHERE id = %s",
                    updates,
                )
                connection.commit()
                print(f"Filled null columns for {len(updates)} rows.")

            cursor.execute("SELECT COUNT(*) FROM students")
            count = cursor.fetchone()[0]
            if count < TOTAL_ROWS:
                rows_to_insert = TOTAL_ROWS - count
                print(f"Inserting {rows_to_insert} duplicate rows to reach {TOTAL_ROWS} rows.")

                cursor.execute(
                    "SELECT name, gender, city, age, marks, birthdate, email, phone, section, stream FROM students LIMIT %s",
                    (BATCH_SIZE,)
                )
                existing_rows = cursor.fetchall()
                sample_data = []
                for i in range(rows_to_insert):
                    row = existing_rows[i % len(existing_rows)]
                    sample_data.append(row)
                    if len(sample_data) >= BATCH_SIZE:
                        cursor.executemany(
                            "INSERT INTO students (name, gender, city, age, marks, birthdate, email, phone, section, stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            sample_data,
                        )
                        connection.commit()
                        sample_data = []

                if sample_data:
                    cursor.executemany(
                        "INSERT INTO students (name, gender, city, age, marks, birthdate, email, phone, section, stream) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        sample_data,
                    )
                    connection.commit()

        cursor.execute("SELECT COUNT(*) FROM students")
        new_count = cursor.fetchone()[0]
        print(f"Done. students table now has {new_count} rows.")
