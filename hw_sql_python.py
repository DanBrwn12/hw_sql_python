import psycopg2
from contextlib import contextmanager
from user_password import password

class DataBase:

    @contextmanager
    def _get_cursor(self):
        """Контекстный менеджер для работы с курсором (приватный)"""
        conn = psycopg2.connect(database="hw_sql_python", user="postgres", password=password)
        with conn.cursor() as cur:
            yield cur
            conn.commit()
        conn.close()


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

    def insert_clients(self, first_name, last_name, email):
        """Добавление новых клиентов"""
        with self._get_cursor() as cur:
            cur.execute("""
            INSERT INTO persons (first_name, last_name, email) VALUES (%s, %s, %s) RETURNING id
            """, (first_name, last_name, email))
            person_id = cur.fetchone()[0]
            print(f"Добавлен клиент c ID: ", person_id)
            return person_id

    def insert_phones(self, person_id, phone_number):
        """Добавление номера телефона клиенту"""
        with self._get_cursor() as cur:
            cur.execute("""
            INSERT INTO phones (person_id, phone_number) VALUES (%s, %s)
            """, (person_id, phone_number))
            print(f"Добавлен номер телефона {phone_number} для клиента {person_id}")

    def update_clients(self, person_id, first_name=None, last_name=None, email=None):
        """Обновление данных о клиенте"""
        updates = []
        params = []

        if first_name is not None:
            updates.append("first_name=%s")
            params.append(first_name)
        if last_name is not None:
            updates.append("last_name=%s")
            params.append(last_name)
        if email is not None:
            updates.append("email=%s")
            params.append(email)

        if not updates:
            return False

        params.append(person_id)
        with self._get_cursor() as cur:
            query = f"""UPDATE persons SET {', '.join(updates)} WHERE id=%s"""
            cur.execute(query, params)
            print(f"Обновлены данные клиента {person_id}")

    def delete_phone(self, person_id, phone_number):
        """Удаление телефона клиента"""
        with self._get_cursor() as cur:
            cur.execute("""
            DELETE FROM phones WHERE person_id=%s AND phone_number=%s
            """, (person_id, phone_number))
            print(f"Удален номер телефона {phone_number} клиента {person_id}")

    def delete_client(self, person_id):
        """Удаление клиента"""
        with self._get_cursor() as cur:
            cur.execute("""
            DELETE FROM persons WHERE id=%s
            """, (person_id,))
            print(f"Клиент {person_id} удален")

    def find_client(self, first_name=None, last_name=None, email=None, phone_number=None):
        search_data = []
        params = []
        joins = []

        if first_name is not None:
            search_data.append("first_name=%s")
            params.append(first_name)
        if last_name is not None:
            search_data.append("last_name=%s")
            params.append(last_name)
        if email is not None:
            search_data.append("email=%s")
            params.append(email)
        if phone_number is not None:
            search_data.append("phone_number=%s")
            params.append(phone_number)
            joins.append("JOIN phones ph ON p.id = ph.person_id")

        if not search_data:
            return False

        with self._get_cursor() as cur:
            query = (f"""SELECT DISTINCT p.id, p.first_name, p.last_name, p.email
                     FROM persons p {', '.join(joins)}
                     WHERE {' AND '.join(search_data)}""")
            cur.execute(query, params)
            print(f"Найдено клиентов {cur.fetchall()}")



if __name__ == '__main__':
    db = DataBase()
    db.create_tables()
    person_1 = db.insert_clients("Иван", "Иванов", "ivaiva@ya.ru")
    db.insert_phones(person_1, "+79993222214")
    db.insert_phones(person_1, "+79993333445")

    person_2 = db.insert_clients("Слава", "Петров", "slpetro2010@gmail.com")

    db.update_clients(person_2,last_name="Сидоров", email="slsidor2012@gmail.com")

    db.delete_phone(person_1, "+79993222214")

    person_3 = db.insert_clients("Лилия", "Заречная", "vsempoka@mail.ru")
    db.delete_client(person_3)

    person_4 = db.insert_clients("Слава", "Иванов", email="sliva@yahoo.com")
    db.insert_phones(person_4, "+79993333445")
    db.find_client(first_name="Слава")
    db.find_client(last_name="Иванов")
    db.find_client(phone_number="+79993333445")


