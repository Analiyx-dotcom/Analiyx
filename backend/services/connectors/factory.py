from .base import BaseConnector
from .postgresql import PostgreSQLConnector
from .mysql import MySQLConnector

_REGISTRY = {
    "postgresql": PostgreSQLConnector,
    "mysql": MySQLConnector,
}


class ConnectorFactory:
    @staticmethod
    def create(db_type: str, config: dict) -> BaseConnector:
        cls = _REGISTRY.get(db_type.lower())
        if cls is None:
            raise ValueError(f"Unsupported database type: {db_type}. Supported: {list(_REGISTRY.keys())}")
        return cls(config)

    @staticmethod
    def supported_types():
        return list(_REGISTRY.keys())
