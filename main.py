import psycopg2
from contextlib import contextmanager
from user_password import password

class DataBase:

    @contextmanager
    def _get_cursor(self):
        """Контекстный менеджер для работы с курсором (приватный)"""
        conn = psycopg2.connect(database="hw_sql_python", user="postgres", password=password)


    def create_tables(self):
        """Сооздание таблиц"""
        with self._get_cursor() as cur:
               cur.execute("""
                DROP TABLE phones;
                DROP TABLE persons;
                """)
               cur.execute("""
                CREATE TABLE IF NOT EXISTS persons(
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(40) NOT NULL,
                    last_name VARCHAR(40) NOT NULL,
                    email VARCHAR(100) NOT NULL
                    )
                    """)
               cur.execute("""
                CREATE TABLE IF NOT EXISTS phones(
                    id SERIAL PRIMARY KEY,
                    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
                    phone_number VARCHAR(20) NOT NULL,
                    CONSTRAINT unique_phone UNIQUE (person_id, phone_number)
                    )
                    """)
                # conn.commit()

    def insert_tables(self):
        pass


