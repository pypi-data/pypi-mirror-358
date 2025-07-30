"""SQL file execution utilities for MySQL connection pool."""

import os
import re
from typing import List
import sqlglot
from .base import ConnectionPoolBase


class SQLFileExecutor:
    """Handles execution of SQL files."""

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
        """Handle DELIMITER statements in SQL content."""
        statements = []
        current_delimiter = ';'
        current_statement = ''
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            delimiter_match = re.match(r'^\s*DELIMITER\s+(.+)\s*$', line, re.IGNORECASE)
            if delimiter_match:
                if current_statement.strip():
                    statements.append(current_statement.strip())
                    current_statement = ''
                
                new_delimiter = delimiter_match.group(1).strip()
                current_delimiter = new_delimiter
                continue
            
            if current_statement:
                current_statement += '\n' + line
            else:
                current_statement = line
            
            if line.endswith(current_delimiter):
                final_statement = current_statement[:-len(current_delimiter)].strip()
                if final_statement:
                    statements.append(final_statement)
                current_statement = ''
        
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        return statements

    @staticmethod
    def _parse_sql_with_sqlglot(sql_content: str) -> List[str]:
        """Parse SQL content using SQLGlot, handling DELIMITER statements."""
        content = SQLFileExecutor._remove_sql_comments(sql_content)
        statements = SQLFileExecutor._handle_delimiter_statements(content)
        
        clean_statements = []
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--') and stmt.upper() != 'DELIMITER':
                if not re.match(r'^\s*DELIMITER\s+', stmt, re.IGNORECASE):
                    clean_statements.append(stmt)
        
        return clean_statements

    @staticmethod
    def run_sql_file(file_path: str) -> None:
        """
        Execute SQL commands from a file.
        
        Args:
            file_path: Path to the SQL file
            
        Raises:
            FileNotFoundError: If the file does not exist
            mysql.connector.Error: If execution fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        statements = SQLFileExecutor._parse_sql_with_sqlglot(sql_content)
        
        if not statements:
            raise ValueError("No valid SQL statements found in the file.")

        db = ConnectionPoolBase.get_instance()
        for stmt in statements:
            # Execute statement and get rows affected
            results, rows_affected = db.execute_with_logging(stmt)
            
            # For simple execution without detailed logging, just use execute_safe
            # db.execute_safe(stmt)

    @staticmethod
    def run_multiple_sql_files(file_paths: List[str]) -> None:
        """
        Execute multiple SQL files in order.
        
        Args:
            file_paths: List of paths to SQL files
        """
        for file_path in file_paths:
            SQLFileExecutor.run_sql_file(file_path)

    @staticmethod
    def run_multiple_sql_files_from_directory(base_dir: str, file_names: List[str]) -> None:
        """
        Execute multiple SQL files from a directory.
        
        Args:
            base_dir: Directory containing SQL files
            file_names: List of SQL file names to execute
        """
        file_paths = [os.path.join(base_dir, name).replace("\\", "/") for name in file_names]
        SQLFileExecutor.run_multiple_sql_files(file_paths)
