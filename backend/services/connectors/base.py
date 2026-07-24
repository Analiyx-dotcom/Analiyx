from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseConnector(ABC):
    """Abstract base class for all external database connectors."""

    def __init__(self, config: dict):
        self.config = config
        self._connection = None

    @abstractmethod
    async def test_connection(self) -> dict:
        """Test connectivity. Returns {'success': bool, 'message': str, 'latency_ms': float}."""

    @abstractmethod
    async def get_schemas(self) -> List[str]:
        """Return list of schema names."""

    @abstractmethod
    async def get_tables(self, schema: str) -> List[Dict[str, Any]]:
        """Return list of tables in a schema: [{'name': str, 'type': 'table'|'view', 'row_estimate': int}]."""

    @abstractmethod
    async def get_columns(self, schema: str, table: str) -> List[Dict[str, Any]]:
        """Return columns: [{'name': str, 'data_type': str, 'nullable': bool, 'is_primary': bool, 'default': str|None}]."""

    @abstractmethod
    async def execute_query(self, sql: str, params: Optional[dict] = None, limit: int = 1000) -> Dict[str, Any]:
        """Execute read-only SQL. Returns {'columns': [...], 'rows': [...], 'row_count': int, 'execution_time_ms': float}."""

    @abstractmethod
    async def get_sample_data(self, schema: str, table: str, limit: int = 100) -> Dict[str, Any]:
        """Get sample rows from a table."""

    @abstractmethod
    async def get_row_count(self, schema: str, table: str) -> int:
        """Get exact or estimated row count."""

    @abstractmethod
    async def get_column_stats(self, schema: str, table: str, column: str) -> Dict[str, Any]:
        """Get column statistics: distinct count, null count, min, max, etc."""

    async def close(self):
        """Close any open connections."""
        self._connection = None
