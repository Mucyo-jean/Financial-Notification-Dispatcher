import sqlite3


class SQLiteWalletRepository:

    def __init__(self):
        self.connection = sqlite3.connect(":memory:")

        self.connection.execute("""
            CREATE TABLE messages(
                msg_id TEXT,
                phone TEXT,
                status TEXT
            )
        """)

        self.connection.commit()


    def get_status(self, msg_id):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT status FROM messages WHERE msg_id=?",
            (msg_id,)
        )

        result = cursor.fetchone()

        if result:
            return result[0]

        return None


    def save_status(self, msg_id, phone, status):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO messages
            (msg_id, phone, status)
            VALUES (?, ?, ?)
            """,
            (msg_id, phone, status)
        )

        self.connection.commit()