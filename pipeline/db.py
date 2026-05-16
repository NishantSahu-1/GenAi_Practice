import os
from dotenv import load_dotenv
import mysql.connector
import logging

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.db_host = os.getenv("MYSQL_HOST", os.getenv("DB_HOST", "localhost"))
        self.db_port = int(os.getenv("MYSQL_PORT", os.getenv("DB_PORT", 3306)))
        self.db_user = os.getenv("MYSQL_USER", os.getenv("DB_USER"))
        self.db_password = os.getenv("MYSQL_PASSWORD", os.getenv("DB_PASSWORD"))
        self.db_name = os.getenv("MYSQL_DATABASE", os.getenv("DB_NAME"))

        if not self.db_user or not self.db_password or not self.db_name:
            raise ValueError(
                "Missing MySQL credentials in .env or environment variables."
            )

        try:
            self.connection = mysql.connector.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
            )
            logging.info("Database connection established successfully")
        except Exception as e:
            self.connection = None
            logging.error(
                f"Failed to connect to the database. Please check the credentials and database status. Error: {e}"
            )

    def execute_query(self, query):
        if self.connection is None:
            return False, "Failed to connect to database"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description] if cursor.description else []
            return True, rows, columns
        except Exception as e:
            logging.error(f"Failed to execute the query. Error: {e}")
            return False, str(e)
