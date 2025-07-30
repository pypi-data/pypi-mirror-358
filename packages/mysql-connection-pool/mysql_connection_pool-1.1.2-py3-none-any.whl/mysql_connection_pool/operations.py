"""Database operations for MySQL connection pool."""

from typing import Optional, Dict, Any, Tuple, Union, List
import mysql.connector
from .base import ConnectionPoolBase
from .logger import MySQLConnectionPoolLogger


class DatabaseOperations(ConnectionPoolBase):
    """Handles basic database operations."""

    def switch_database(self, database: str) -> None:
        """
        Switch to a different database for all subsequent queries.
        
        Args:
            database: Name of the database to switch to
            
        Raises:
            mysql.connector.Error: If database doesn't exist or connection fails
            ValueError: If database name contains invalid characters
        """
        if not self._validate_db_name(database):
            raise ValueError("Invalid database name. Only alphanumeric characters and underscores are allowed.")
            
        conn = self._get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{database}`")
                self._current_database = database
                # Update connection params for new connections
                self._connection_params['database'] = database
        finally:
            conn.close()

    def get_current_database(self) -> Optional[str]:
        """
        Get the name of the currently active database.
        
        Returns:
            str: Current database name or None if not connected to any database
        """
        return self._current_database

    def execute(
        self, 
        query: str, 
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Tuple['mysql.connector.cursor.MySQLCursor', 'mysql.connector.connection.MySQLConnection']:
        """
        Execute SQL query and return cursor and connection.
        
        Note: Caller MUST close the connection manually.
        
        Args:
            query: SQL query with optional parameters (%s or %(name)s)
            params: Query parameters
            database: Optional database to use for this query
            enable_logging: Whether to log this execution
            
        Returns:
            Tuple (cursor, connection) - You must call connection.close() after
            
        Example:
            >>> cursor, conn = db.execute("SELECT * FROM users WHERE id = %s", (1,))
            >>> try:
            ...     results = cursor.fetchall()
            ... finally:
            ...     conn.close()
        """
        conn = self._get_connection()
        if database:
            with conn.cursor() as cursor:
                cursor.execute(f"USE `{database}`")
        cursor = conn.cursor(dictionary=self._dictionary)
        norm_params = self._normalize_params(params)
        
        try:
            if norm_params is not None:
                cursor.execute(query, norm_params)
            else:
                cursor.execute(query)
            
            # Log if enabled
            if enable_logging:
                MySQLConnectionPoolLogger.log_statement_execution(
                    statement_num=1,
                    total_statements=1,
                    query=query,
                    success=True,
                    rows_affected=cursor.rowcount,
                    execution_context="execute"
                )
        except Exception as e:
            if enable_logging:
                MySQLConnectionPoolLogger.log_statement_execution(
                    statement_num=1,
                    total_statements=1,
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="execute"
                )
            conn.close()  # Close on error since user can't handle it
            raise e
            
        return cursor, conn

    def execute_safe(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Optional[List[Dict]]:
        """
        Execute query and automatically close resources.
        
        Args:
            query: SQL query
            params: Query parameters
            database: Optional database to use for this query
            enable_logging: Whether to log this execution
            
        Returns:
            List of results or None for non-result queries
            
        Example:
            >>> results = db.execute_safe("SELECT * FROM products", database='inventory')
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
                
                # Log if enabled
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

    def fetchone(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Execute query and return a single row.
        
        Args:
            query: SQL query
            params: Query parameters
            database: Optional database to use for this query
            enable_logging: Whether to log this execution
            
        Returns:
            Dict with row data or None if no results
            
        Example:
            >>> user = db.fetchone("SELECT * FROM users WHERE id = %s", (1,), database='auth_db')
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
                result = cursor.fetchone()
                rows_affected = cursor.rowcount
                
                # Log if enabled
                if enable_logging:
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=1,
                        total_statements=1,
                        query=query,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="fetchone"
                    )
                
                return result
        except Exception as e:
            if enable_logging:
                MySQLConnectionPoolLogger.log_statement_execution(
                    statement_num=1,
                    total_statements=1,
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="fetchone"
                )
            raise e
        finally:
            conn.close()

    def fetchall(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Execute query and return all rows.
        
        Args:
            query: SQL query
            params: Query parameters
            database: Optional database to use for this query
            enable_logging: Whether to log this execution
            
        Returns:
            List[Dict] with results
            
        Example:
            >>> products = db.fetchall("SELECT * FROM products", database='store_db')
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
                results = cursor.fetchall()
                rows_affected = cursor.rowcount
                
                # Log if enabled
                if enable_logging:
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=1,
                        total_statements=1,
                        query=query,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="fetchall"
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
                    execution_context="fetchall"
                )
            raise e
        finally:
            conn.close()

    def commit_execute(
        self,
        query: str,
        params: Optional[Union[Tuple, Dict]] = None,
        database: Optional[str] = None,
        enable_logging: bool = False
    ) -> Tuple[int, Optional[int]]:
        """
        Execute write query and commit.
        
        Args:
            query: SQL query (INSERT/UPDATE/DELETE)
            params: Query parameters
            database: Optional database to use for this query
            enable_logging: Whether to log this execution
            
        Returns:
            Tuple (rowcount, lastrowid)
            
        Example:
            >>> count, last_id = db.commit_execute(
            ...     "INSERT INTO logs (message) VALUES (%s)",
            ...     ("Error 404",),
            ...     database='logging_db'
            ... )
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
                
                # Log if enabled
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

    @staticmethod
    def lastrowid(cursor: mysql.connector.cursor.MySQLCursor) -> Optional[int]:
        """Return the ID of the last inserted row."""
        return cursor.lastrowid    @staticmethod
    def rowcount(cursor: mysql.connector.cursor.MySQLCursor) -> int:
        """Return the number of affected rows."""
        return cursor.rowcount

    # Convenience methods with logging enabled by default
    def execute_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Tuple['mysql.connector.cursor.MySQLCursor', 'mysql.connector.connection.MySQLConnection']:
        """Execute SQL query with logging enabled."""
        return self.execute(query, params, database, enable_logging=True)
    
    def execute_safe_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Optional[List[Dict]]:
        """Execute query safely with logging enabled."""
        return self.execute_safe(query, params, database, enable_logging=True)
    
    def fetchone_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch one row with logging enabled."""
        return self.fetchone(query, params, database, enable_logging=True)
    
    def fetchall_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all rows with logging enabled."""
        return self.fetchall(query, params, database, enable_logging=True)
    
    def commit_execute_logged(self, query: str, params: Optional[Union[Tuple, Dict]] = None, database: Optional[str] = None) -> Tuple[int, Optional[int]]:
        """Execute write query with commit and logging enabled."""
        return self.commit_execute(query, params, database, enable_logging=True)
