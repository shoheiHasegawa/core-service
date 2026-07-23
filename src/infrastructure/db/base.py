from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def setup_sqlite_pragma(engine):
    """
    SQLiteエンジンに対してWALモードなどのPRAGMA設定を適用します。
    DI経由で生成されたエンジンを渡して初期化してください。
    """

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()
