import mysql.connector.pooling
import threading
from typing import Optional, Dict, Any, Tuple, Union, List
from .mysql_connection_pool_logger import MySQLConnectionPoolLogger


class MySQLConnectionPool:
    """
    A thread-safe MySQL connection pool manager with database switching capability.
    
    Provides a high-level interface for executing SQL queries with automatic:
    - Connection pooling
    - Resource cleanup (cursors and connections)
    - Transaction management
    - Automatic reconnection
    - Database switching
    - Beautiful logging with multilingual support
    """
    
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
        """
        with MySQLConnectionPool._lock:
            if MySQLConnectionPool._pool is None:
                MySQLConnectionPool._dictionary = dictionary
                MySQLConnectionPool._current_database = database
                MySQLConnectionPool._log_language = log_language
                MySQLConnectionPool._log_file_path = logs
                
                # Setup logger with new parameters
                MySQLConnectionPoolLogger.setup_logger(
                    log_file_path=logs,
                    language=log_language,
                    clear_logs=clear_logs
                )
                
                MySQLConnectionPool._connection_params = {
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
                MySQLConnectionPool._connection_params.update(kwargs)
                
                MySQLConnectionPool._pool = mysql.connector.pooling.MySQLConnectionPool(
                    **MySQLConnectionPool._connection_params
                )
                MySQLConnectionPool._instance = self

    def switch_database(self, database: str) -> None:
        """
        Switch to a different database for all subsequent queries.
        """
        if not self._validate_db_name(database):
            raise ValueError("Invalid database name. Only alphanumeric characters and underscores are allowed.")
            
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{database}`")
                MySQLConnectionPool._current_database = database
                # Update connection params for new connections
                MySQLConnectionPool._connection_params['database'] = database
        finally:
            conn.close()

    def _validate_db_name(self, name: str) -> bool:
        """Validate database name to prevent SQL injection"""
        return all(c.isalnum() or c == '_' for c in name)

    def get_current_database(self) -> Optional[str]:
        """
        Get the name of the currently active database.
        """
        return self._current_database

    def _get_connection(self) -> mysql.connector.connection.MySQLConnection:
        """
        Get a connection from the pool and ensure it's using the correct database.
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

    def soft_execute(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Execute query without commit (for reads or operations within a transaction).
        """
        return self._execute_safe(query, params, database, enable_logging=False)

    def hard_execute(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Tuple[int, Optional[int]]:
        """
        Execute query with commit (for writes that need immediate persistence).
        """
        return self._commit_execute(query, params, database, enable_logging=False)

    def soft_execute_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Optional[List[Dict]]:
        """
        Execute query without commit and with logging.
        """
        return self._execute_safe(query, params, database, enable_logging=True)

    def hard_execute_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Tuple[int, Optional[int]]:
        """
        Execute query with commit and with logging.
        """
        return self._commit_execute(query, params, database, enable_logging=True)

    def _execute_safe(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Optional[List[Dict]]:
        """
        Internal implementation of safe execution.
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
                rows_affected = cursor.rowcount
                
                if enable_logging:
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=1,
                        total_statements=1,
                        query=query,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="execute_safe"
                    )
                
                return results
        except Exception as e:
            if enable_logging:
                MySQLConnectionPoolLogger.log_statement_execution(
                    statement_num=1,
                    total_statements=1,
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="execute_safe"
                )
            raise e
        finally:
            conn.close()

    def _commit_execute(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Tuple[int, Optional[int]]:
        """
        Internal implementation of commit execution.
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
                conn.commit()
                rows_affected = cursor.rowcount
                last_id = cursor.lastrowid
                
                if enable_logging:
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=1,
                        total_statements=1,
                        query=query,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="commit_execute"
                    )
                
                return rows_affected, last_id
        except Exception as e:
            if enable_logging:
                MySQLConnectionPoolLogger.log_statement_execution(
                    statement_num=1,
                    total_statements=1,
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="commit_execute"
                )
            raise e
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