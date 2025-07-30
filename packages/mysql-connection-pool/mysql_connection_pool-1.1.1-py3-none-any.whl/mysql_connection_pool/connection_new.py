"""MySQL Connection Pool with database switching capability."""

from .operations import DatabaseOperations
from .sql_executor import SQLFileExecutor
from .logger import MySQLConnectionPoolLogger


class MySQLConnectionPool(DatabaseOperations):
    """
    A thread-safe MySQL connection pool manager with database switching capability.
    """
    
    # SQL file execution methods
    @staticmethod
    def run_sql_file(file_path: str) -> None:
        """Execute SQL commands from a file with logging."""
        SQLFileExecutor.run_sql_file(file_path)

    @staticmethod
    def run_multiple_sql_files(file_paths: list) -> None:
        """Execute multiple SQL files in order with logging."""
        SQLFileExecutor.run_multiple_sql_files(file_paths)

    @staticmethod
    def run_multiple_sql_files_from_directory(base_dir: str, file_names: list) -> None:
        """Execute multiple SQL files from a directory with logging."""
        SQLFileExecutor.run_multiple_sql_files_from_directory(base_dir, file_names)

    def soft_execute(self, query: str, params=None, database: str = None, enable_logging: bool = False):
        """
        Execute a read-only SQL query (no commit, doesn't modify database).
        Returns results or None if no results.
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
                
                # Consume all results to avoid "Unread result found" errors
                results = cursor.fetchall() if cursor.with_rows else None
                if cursor.with_rows and not results:
                    # For queries that return results but fetchall returns None/empty
                    while cursor.nextset():
                        pass
                
                rows_affected = cursor.rowcount
                
                if enable_logging:
                    MySQLConnectionPoolLogger.log_operation(
                        operation_type="soft_execute",
                        query=query,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="soft_execute"
                    )
                
                return results
        except Exception as e:
            if enable_logging:
                MySQLConnectionPoolLogger.log_operation(
                    operation_type="soft_execute",
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="soft_execute"
                )
            raise e
        finally:
            # Ensure connection is properly closed
            try:
                conn.close()
            except:
                pass

    def hard_execute(self, query: str, params=None, database: str = None, enable_logging: bool = False):
        """
        Execute a SQL query that modifies the database (does commit).
        Returns (rowcount, lastrowid) for write operations.
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
                
                # For write operations, consume any unread results
                if cursor.with_rows:
                    cursor.fetchall()
                    while cursor.nextset():
                        pass
                
                conn.commit()
                
                result = (cursor.rowcount, cursor.lastrowid)
                
                if enable_logging:
                    MySQLConnectionPoolLogger.log_operation(
                        operation_type="hard_execute",
                        query=query,
                        success=True,
                        rows_affected=cursor.rowcount,
                        execution_context="hard_execute"
                    )
                
                return result
        except Exception as e:
            try:
                conn.rollback()
            except:
                pass
                
            if enable_logging:
                MySQLConnectionPoolLogger.log_operation(
                    operation_type="hard_execute",
                    query=query,
                    success=False,
                    error_msg=str(e),
                    execution_context="hard_execute"
                )
            raise e
        finally:
            # Ensure connection is properly closed
            try:
                conn.close()
            except:
                pass

    # Convenience methods with logging enabled by default
    def soft_execute_logged(self, query: str, params=None, database: str = None):
        """Execute read-only query with logging enabled."""
        return self.soft_execute(query, params, database, enable_logging=True)
    
    def hard_execute_logged(self, query: str, params=None, database: str = None):
        """Execute write query with logging enabled."""
        return self.hard_execute(query, params, database, enable_logging=True)