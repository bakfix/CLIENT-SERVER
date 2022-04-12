import sqlite3


class DataOrders:

    def __init__(self, database: str = "DataOrders.sqlite"):
        self._db = database
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS Orders  (
                              id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                              location TEXT NOT NULL,
                              description TEXT NOT NULL,
                              price INTEGER NOT NULL,
                              worker_id INTEGER,
                              is_active BOOLEAN NOT NULL);""")
            connection.commit()

    def get_orders(self) -> list:
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            result = cursor.execute("""SELECT id, location, description, price
                                        FROM Orders WHERE worker_id IS NULL;""").fetchall()
            return result

    def add_new_orders(self, location, description, price) -> bool:
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""INSERT INTO Orders (location, description, price, worker_id, is_active)
                                VALUES (?, ?, ?, NULL, 0)""", (location, description, price))
            connection.commit()

    def take_orders(self, orders_id, worker_id) -> bool:
        if self._orders_is_free(orders_id):
            self._set_orders_worker(orders_id, worker_id)
            return True
        return False

    def report_about_orders(self, orders_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE Orders SET is_active=1 WHERE id=?""", (orders_id,))
            connection.commit()

    def _orders_is_free(self, orders_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            worker_id = cursor.execute("""SELECT worker_id FROM Orders WHERE id = ?""",
                                       (orders_id,)).fetchone()[0]
        return True if worker_id is None else False

    def _set_orders_worker(self, orders_id, worker_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            cursor.execute("""UPDATE Orders SET worker_id=? WHERE id=?""", (worker_id, orders_id))
            connection.commit()

    def get_worker_orders(self, worker_id):
        with sqlite3.connect(self._db) as connection:
            cursor = connection.cursor()
            result = cursor.execute("""SELECT id, location, description, price
                                        FROM Orders WHERE worker_id=?;""", (worker_id,)).fetchall()
            return result
