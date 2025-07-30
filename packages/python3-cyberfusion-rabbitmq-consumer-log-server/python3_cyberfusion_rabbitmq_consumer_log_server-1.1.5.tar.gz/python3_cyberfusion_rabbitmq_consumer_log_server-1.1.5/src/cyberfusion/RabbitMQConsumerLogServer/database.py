import sqlite3
from datetime import datetime
from sqlalchemy.pool.base import _ConnectionRecord
from sqlalchemy import ForeignKey, MetaData
from cyberfusion.RabbitMQConsumerLogServer.settings import settings
from sqlalchemy import create_engine, Column, DateTime, Integer, String
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import event


def set_sqlite_pragma(
    dbapi_connection: sqlite3.Connection, connection_record: _ConnectionRecord
) -> None:
    """Enable foreign key support.

    This is needed for cascade deletes to work.

    See https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys
    """
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA foreign_keys=ON")

    cursor.close()


def make_database_session() -> Session:
    engine = create_engine("sqlite:///" + settings.database_path)

    event.listen(engine, "connect", set_sqlite_pragma)

    return sessionmaker(bind=engine)()


naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)

Base = declarative_base(metadata=metadata)


class BaseModel(Base):  # type: ignore[misc, valid-type]
    """Base model."""

    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class RPCRequestLog(BaseModel):
    """RPC request log model."""

    __tablename__ = "rpc_requests_logs"

    correlation_id = Column(String(length=36), unique=True, nullable=False)
    request_payload = Column(String(), nullable=False)
    virtual_host_name = Column(String(length=255), nullable=False)
    exchange_name = Column(String(length=255), nullable=False)
    queue_name = Column(String(length=255), nullable=False)
    hostname = Column(String(length=255), nullable=False)
    rabbitmq_username = Column(String(length=255), nullable=False)


class RPCResponseLog(BaseModel):
    """RPC response log model."""

    __tablename__ = "rpc_responses_logs"

    correlation_id = Column(
        String(length=36),
        ForeignKey("rpc_requests_logs.correlation_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    response_payload = Column(String(), nullable=False)
    traceback = Column(String(), nullable=True)
