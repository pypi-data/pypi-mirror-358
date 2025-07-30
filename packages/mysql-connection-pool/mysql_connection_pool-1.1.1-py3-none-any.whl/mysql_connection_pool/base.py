"""Base class for MySQL connection pool with thread-safe connection management."""

import mysql.connector.pooling
import threading
from typing import Optional, Dict, Any, Union, Tuple, List


class ConnectionPoolBase:
    """Base class for MySQL connection pool management."""
    
    _pool: mysql.connector.pooling.MySQLConnectionPool = None
    _lock: threading.Lock = threading.Lock()
    _dictionary: bool = True
    _instance = None
    _current_database: Optional[str] = None
    _connection_params: Dict[str, Any] = {}
    _log_language: str = "es"
    _log_file_path: Optional[str] = None

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        dictionary: bool = True,
        pool_name: str = "mysql_pool",
        pool_size: int = 5,
        logs: Optional[str] = None,
        log_language: str = "es",
        clear_logs: bool = False,
        **kwargs
    ):
        """
        Initialize the connection pool (once per application).
        
        Args:
            host: MySQL server host
            port: MySQL port (default 3306)
            user: MySQL username
            password: MySQL password
            database: Database to use
            dictionary: If True, returns results as dicts
            pool_name: Pool identifier name
            pool_size: Maximum connections in pool
            logs: Log file path (None=no logging, "logs/file.log"=relative, "/path/file.log"=absolute)
            log_language: Language for log messages "es" or "en" (default "es")
            clear_logs: If True, clears the log file content at startup (default False)
            **kwargs: Additional connection parameters
            
        Raises:
            mysql.connector.Error: If initial connection fails
        """
        with ConnectionPoolBase._lock:
            if ConnectionPoolBase._pool is None:
                ConnectionPoolBase._dictionary = dictionary
                ConnectionPoolBase._current_database = database
                ConnectionPoolBase._log_language = log_language
                ConnectionPoolBase._log_file_path = logs

                # Import here to avoid circular import
                from .logger import MySQLConnectionPoolLogger
                # Setup logger with new parameters
                MySQLConnectionPoolLogger.setup_logger(
                    log_file_path=logs,
                    language=log_language,
                    clear_logs=clear_logs
                )
                
                ConnectionPoolBase._connection_params = {
                    'host': host,
                    'port': port,
                    'user': user,
                    'password': password,
                    'database': database,
                    'pool_name': pool_name,
                    'pool_size': pool_size,
                    'autocommit': True,
                    'pool_reset_session': True,
                }
                ConnectionPoolBase._connection_params.update(kwargs)
                
                ConnectionPoolBase._pool = mysql.connector.pooling.MySQLConnectionPool(
                    **ConnectionPoolBase._connection_params
                )
                ConnectionPoolBase._instance = self

    def _validate_db_name(self, name: str) -> bool:
        """Validate database name to prevent SQL injection"""
        return all(c.isalnum() or c == '_' for c in name)

    def _get_connection(self) -> mysql.connector.connection.MySQLConnection:
        """
        Get a connection from the pool and ensure it's using the correct database.
        
        Returns:
            MySQLConnection: Active connection
            
        Raises:
            PoolError: If no connections available after timeout
        """
        conn = self._pool.get_connection()
        if self._current_database:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"USE `{self._current_database}`")
            except Exception:
                conn.close()
                raise
        return conn

    def _normalize_params(self, params):
        """Helper to normalize query parameters for cursor.execute."""
        if params is None:
            return None
        if isinstance(params, (tuple, list, dict)):
            return params
        # Single value, wrap in tuple
        return (params,)

    def execute_with_logging(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Tuple[Optional[List[Dict]], int]:
        """
        Execute query and return results along with row count for logging.
        
        Args:
            query: SQL query
            params: Query parameters
            database: Optional database to use for this query
            
        Returns:
            Tuple (results, rowcount)
        """
        conn = self._get_connection()
        try:
            if database:
                with conn.cursor() as cursor:
                    cursor.execute(f"USE `{database}`")
            with conn.cursor(dictionary=self._dictionary) as cursor:
                norm_params = self._normalize_params(params)
                if norm_params is not None:
                    cursor.execute(query, norm_params)
                else:
                    cursor.execute(query)
                results = cursor.fetchall() if cursor.with_rows else None
                row_count = cursor.rowcount
                return results, row_count
        finally:
            conn.close()

    @classmethod
    def is_initialized(cls) -> bool:
        """Check if the pool has been initialized."""
        return cls._pool is not None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        if not cls._pool or not cls._instance:
            raise RuntimeError("Pool not initialized. Call __init__ first.")
        return cls._instance