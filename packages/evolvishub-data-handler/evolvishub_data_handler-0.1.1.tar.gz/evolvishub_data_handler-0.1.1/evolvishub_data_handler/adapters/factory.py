from typing import Dict, Type
from ..config import DatabaseConfig, DatabaseType
from .base import BaseAdapter
from .postgresql import PostgreSQLAdapter
from .mysql import MySQLAdapter
from .sqlite import SQLiteAdapter
from .oracle import OracleAdapter
from .mongodb import MongoDBAdapter
from .file import FileAdapter
from .s3 import S3Adapter


class AdapterFactory:
    """Factory class for creating database adapters."""
    
    _adapters: Dict[DatabaseType, Type[BaseAdapter]] = {
        DatabaseType.POSTGRESQL: PostgreSQLAdapter,
        DatabaseType.MYSQL: MySQLAdapter,
        DatabaseType.SQLITE: SQLiteAdapter,
        DatabaseType.ORACLE: OracleAdapter,
        DatabaseType.MONGODB: MongoDBAdapter,
        DatabaseType.FILE: FileAdapter,
        DatabaseType.S3: S3Adapter,
    }

    @classmethod
    def create(cls, config: DatabaseConfig) -> BaseAdapter:
        """Create a database adapter based on the configuration.
        
        Args:
            config: Database configuration object.
            
        Returns:
            An instance of the appropriate database adapter.
            
        Raises:
            ValueError: If the database type is not supported.
        """
        adapter_class = cls._adapters.get(config.type)
        if not adapter_class:
            raise ValueError(f"Unsupported database type: {config.type}")
        
        return adapter_class(config) 