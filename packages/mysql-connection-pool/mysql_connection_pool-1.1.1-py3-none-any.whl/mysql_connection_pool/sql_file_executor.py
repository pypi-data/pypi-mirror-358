import os
import re
import sqlglot
from typing import List
from .mysql_connection_pool import MySQLConnectionPool
from .mysql_connection_pool_logger import MySQLConnectionPoolLogger


class SQLFileExecutor:
    @staticmethod
    def _remove_sql_comments(sql_content: str) -> str:
        """Remove SQL comments while preserving string literals."""
        # Remove single line comments (-- comment)
        sql_content = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)
        
        # Remove multi-line comments (/* comment */)
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        return sql_content

    @staticmethod
    def _handle_delimiter_statements(content: str) -> List[str]:
        """
        Handle DELIMITER statements in SQL content.
        """
        statements = []
        current_delimiter = ';'
        current_statement = ''
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check for DELIMITER change
            delimiter_match = re.match(r'^\s*DELIMITER\s+(.+)\s*$', line, re.IGNORECASE)
            if delimiter_match:
                # Save current statement if exists
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ''
                
                # Change delimiter
                new_delimiter = delimiter_match.group(1).strip()
                current_delimiter = new_delimiter
                continue
            
            # Add line to current statement
            if current_statement:
                current_statement += '\n' + line
            else:
                current_statement = line
            
            # Check if statement ends with current delimiter
            if line.endswith(current_delimiter):
                # Remove the delimiter from the end
                final_statement = current_statement[:-len(current_delimiter)].strip()
                if final_statement:
                    statements.append(final_statement)
                current_statement = ''
        
        # Add any remaining statement
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements

    @staticmethod
    def _parse_sql_with_sqlglot(sql_content: str) -> List[str]:
        """
        Parse SQL content using SQLGlot, handling DELIMITER statements and complex triggers.
        """
        # Remove comments but keep structure
        content = SQLFileExecutor._remove_sql_comments(sql_content)
        
        # Handle DELIMITER statements
        statements = SQLFileExecutor._handle_delimiter_statements(content)
        
        # Clean and validate each statement
        clean_statements = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--') and stmt.upper() != 'DELIMITER':
                # Skip standalone DELIMITER statements
                if not re.match(r'^\s*DELIMITER\s+', stmt, re.IGNORECASE):
                    clean_statements.append(stmt)
        
        return clean_statements
    
    @staticmethod
    def run_sql_file(file_path: str) -> None:
        """
        Execute SQL commands from a file using SQLGlot for advanced parsing.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_content = file.read()

            # Parse SQL content using SQLGlot with DELIMITER support
            statements = SQLFileExecutor._parse_sql_with_sqlglot(sql_content)
            
            if not statements:
                MySQLConnectionPoolLogger.log_warning("No se encontraron sentencias SQL válidas en el archivo.")
                return

            db = MySQLConnectionPool.get_instance()
              # Log file processing start
            MySQLConnectionPoolLogger.log_file_processing(file_path, len(statements), "run_sql_file")
            
            for i, stmt in enumerate(statements, 1):
                try:
                    # Execute statement and get rows affected
                    results, rows_affected = db.execute_with_logging(stmt)
                    
                    # Log successful execution
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=i,
                        total_statements=len(statements),
                        query=stmt,
                        success=True,
                        rows_affected=rows_affected,
                        execution_context="run_sql_file"
                    )
                except Exception as stmt_error:
                    # Log error execution
                    MySQLConnectionPoolLogger.log_statement_execution(
                        statement_num=i,
                        total_statements=len(statements),
                        query=stmt,
                        success=False,
                        error_msg=str(stmt_error),
                        execution_context="run_sql_file"
                    )
                    raise stmt_error
                    
        except Exception as e:
            MySQLConnectionPoolLogger.log_error(
                title="Error procesando archivo",
                error_msg=str(e),
                problematic_content=file_path,
                execution_context="run_sql_file"
            )
            raise e

    @staticmethod
    def run_multiple_sql_files(file_paths: List[str]) -> None:
        """
        Execute multiple SQL files in order.
        """
        db = MySQLConnectionPool.get_instance()
        for file_path in file_paths:
            db.run_sql_file(file_path)
    
    @staticmethod
    def run_multiple_sql_files_from_directory(base_dir: str, file_names: List[str]) -> None:
        """
        Execute multiple SQL files from a directory with beautiful logging.
        """
        file_paths = [os.path.join(base_dir, name).replace("\\", "/") for name in file_names]
          # Log files list
        MySQLConnectionPoolLogger.log_files_list(file_paths, "run_multiple_sql_files_from_directory")
        
        db = MySQLConnectionPool.get_instance()
        db.run_multiple_sql_files(file_paths)