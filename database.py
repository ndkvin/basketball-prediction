import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class Database:
    def __init__(self):
        self._connect()

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME")
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connection = None
            self.cursor = None

    def reconnect(self):
        if self.connection is None or not self.connection.is_connected():
            self._connect()

    def execute_query(self, query, params=None, commit=False):
      self.reconnect()
      try:
          if params:
              self.cursor.execute(query, params)
          else:
              self.cursor.execute(query)
          
          if commit:
              self.connection.commit()  # Commit the transaction if required
          
          return self.cursor
      except mysql.connector.Error as err:
          print(f"Query Error: {err}")
          return None

    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

# Create an instance of the Database class
db = Database()