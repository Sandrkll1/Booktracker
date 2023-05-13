import sqlite3
import os
import json
from datetime import datetime


class BaseDatabase:

    def __init__(self, filename):
        self.filename = filename
        self.db = sqlite3.connect(filename)
        self.cursor = self.db.cursor()

    @staticmethod
    def convert_to_binary_data(filename):
        with open(filename, 'rb') as file:
            blob_data = file.read()
        return blob_data


class UserDatabase(BaseDatabase):

    def __init__(self, filename):
        super().__init__(filename)

    def create_table(self):
        query = """
                   CREATE TABLE IF NOT EXISTS users(
                       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       username VARCHAR(60),
                       password VARCHAR(60) 
                   ); 
                   """

        self.cursor.execute(query)
        self.db.commit()

    def add_user(self, username, password):
        self.cursor.execute("""INSERT INTO users (username, password) VALUES(?, ?)""", (username, password,))
        self.db.commit()

    def get_user(self, username) -> tuple:
        user = self.cursor.execute("""SELECT * FROM users WHERE username = ?""", (username,))
        return user.fetchone()

    def get_user_by_id(self, user_id):
        user = self.cursor.execute("""SELECT * FROM users WHERE user_id =?""", (user_id,))
        return user.fetchone()

    def user_in_db(self, username) -> bool:
        return bool(self.get_user(username))

    def check_user(self, username, password) -> bool:
        user = self.cursor.execute("""SELECT * FROM users WHERE username = ? AND password = ?""", (username, password,))
        return bool(len(user.fetchall()))


class BookDatabase(BaseDatabase):

    def __init__(self, filename):
        super().__init__(filename)

    def create_table(self):
        query = """
                    CREATE TABLE IF NOT EXISTS books(
                        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name VARCHAR(60),
                        description TEXT,
                        timeline_start DATE,
                        timeline_end DATE,
                        notes TEXT,
                        comment TEXT,
                        book_review TEXT,
                        rating DOUBLE,
                        cover BLOB, 
                        is_reading BOOLEAN
                    );    
                """

        self.cursor.execute(query)
        self.db.commit()

    def add_book(self, user_id, book_name, **kwargs):
        """
        :param user_id:
        :param book_name:
        :param kwargs: description, timeline_start, timeline_end, notes, comment, book_review, rating, cover, is_reading
        :return:
        """

        try:
            if os.path.isfile(kwargs["cover"]):
                kwargs["cover"] = self.convert_to_binary_data(kwargs["cover"])
        except Exception:
            pass

        if "cover" not in kwargs:
            kwargs["cover"] = None

        keys = " ".join([k + " ," for k in tuple(kwargs.keys())])[:-1]
        values = "?, " * (len(kwargs) + 2)

        self.cursor.execute(
            f"""INSERT INTO books (user_id, name, {keys}) VALUES({values[:-2]})""",
            (user_id, book_name, *tuple(kwargs.values()),)
        )

        self.db.commit()

    def get_book(self, user_id, book_id):
        book = self.cursor.execute("""SELECT * FROM books WHERE user_id = ? AND book_id = ?""", (user_id, book_id,))
        return book.fetchone()

    def get_all_books(self, user_id):
        books = self.cursor.execute("""SELECT * FROM books WHERE user_id = ?""", (user_id,))
        return books.fetchall()

    def update_book_info(self, user_id, book_id, **kwargs):
        """
        :param user_id:
        :param book_id:
        :param kwargs: description, timeline_start, timeline_end, notes, comment, book_review, rating, cover, is_reading
        :return: None
        """

        if "cover" in kwargs.keys():
            try:
                if os.path.isfile(kwargs["cover"]):
                    kwargs["cover"] = self.convert_to_binary_data(kwargs["cover"])
            except Exception:
                pass

        keys = " ".join([k + " = ?," for k in tuple(kwargs.keys())])[:-1]

        self.cursor.execute(f"""UPDATE books SET {keys} WHERE user_id = ? AND book_id = ?""",
                            (*tuple(kwargs.values()), int(user_id), book_id,))
        self.db.commit()

    def book_in_db(self, user_id, book_id, name) -> bool:
        book = self.cursor.execute(f"SELECT * FROM books WHERE user_id = ? AND book_id = ? AND name = ?",
                                   (user_id, book_id, name,))
        return bool(len(book.fetchall()))

    def delete_book(self, user_id, book_id):
        self.cursor.execute(f"""DELETE FROM books WHERE user_id =? AND book_id =?""", (user_id, book_id,))
        self.db.commit()

    def sort_by(self, user_id, param):
        self.cursor.execute(f"""SELECT * FROM books WHERE user_id =? ORDER BY {param}""", (user_id,))
        return self.cursor.fetchall()

    def search_books_name(self, user_id, name):
        self.cursor.execute("""SELECT * FROM books WHERE user_id = ? AND LOWER(name) LIKE LOWER(?)""", (user_id, f"%{name}%",))
        return self.cursor.fetchall()


class DataBase(UserDatabase, BookDatabase):

    def __init__(self, filename):
        super().__init__(filename)

    def backup(self, user_id, path):
        user = self.get_user_by_id(user_id)
        books = self.get_all_books(user_id)

        books = [
            {
                "book_id": book[0],
                "user_id": book[1],
                "name": book[2],
                "description": book[3],
                "timeline_start": str(book[4]),
                "timeline_end": str(book[5]),
                "notes": book[6],
                "comment": book[7],
                "book_review": book[8],
                "rating": book[9],
                "cover": str(book[10]),
                "is_reading": book[11]
            } for book in books
        ]

        backup_json = {
            "user_id": user[0],
            "username": user[1],
            "password": user[2],
            "books": books
        }

        with open(path + "\\booktracker_backup.json", "w", encoding="utf8") as file:
            json.dump(backup_json, file)

    def restore(self, user_id, path):
        try:
            with open(path, "r", encoding="utf8") as file:
                data = json.load(file)

            for book in data["books"]:

                if not self.book_in_db(user_id, book["book_id"], book["name"]):
                    try:
                        cover = eval(book["cover"]) if book["cover"] is not None else None
                    except Exception:
                        cover = None

                    timeline_start = book["timeline_start"]
                    timeline_end = book["timeline_end"]

                    self.add_book(user_id, book["name"],
                                  description=book["description"],
                                  timeline_start=timeline_start,
                                  timeline_end=timeline_end, notes=book["notes"],
                                  comment=book["comment"],
                                  book_review=book["book_review"], rating=book["rating"],
                                  cover=cover, is_reading=book["is_reading"]
                                  )
        except Exception:
            return False

        return True


if __name__ == "__main__":
    db = DataBase(".\\test.db")
    # db.backup(1)
    # db.add_user("first", "second")
    # db.add_book(1, "lkddyhs", description="i873gbhjygtugil")
    # db.update_book_info(1, "sdfjkfhjkdk", description="888")
