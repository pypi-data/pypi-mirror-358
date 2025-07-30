"""
Custom logger for MySQLConnectionPool with emoji support and multilingual logging.
"""

import logging
import os
from datetime import datetime
from typing import List, Optional, Dict, Any


class MySQLConnectionPoolLogger:
    """
    Custom logger for MySQLConnectionPool with emoji support and logs formatting.
    Logs are saved based on the provided path or current working directory.
    """
    
    _logger = None
    _log_file_path = None
    _language = "es"
    
    # Multilingual messages
    MESSAGES = {
        "es": {
            "processing_file": "Procesando archivo SQL",
            "executing_statements": "Ejecutando sentencias SQL",
            "executing_statement": "Ejecutando sentencia",
            "statement_success": "Sentencia ejecutada correctamente",
            "statement_error": "Error en sentencia",
            "files_to_execute": "Archivos a ejecutar",
            "no_statements": "No se encontraron sentencias SQL válidas",
            "file_error": "Error procesando archivo",
            "problematic_statement": "Sentencia problemática",
            "query": "Consulta",
            "response": "Respuesta",
            "success": "ÉXITO",
            "error": "ERROR",
            "info": "INFO",
            "debug": "DEBUG",
            "soft_execute": "Ejecución de solo lectura",
            "hard_execute": "Ejecución con escritura"
        },
        "en": {
            "processing_file": "Processing SQL file",
            "executing_statements": "Executing SQL statements",
            "executing_statement": "Executing statement",
            "statement_success": "Statement executed successfully",
            "statement_error": "Error in statement",
            "files_to_execute": "Files to execute",
            "no_statements": "No valid SQL statements found",
            "file_error": "Error processing file",
            "problematic_statement": "Problematic statement",
            "query": "Query",
            "response": "Response",
            "success": "SUCCESS",
            "error": "ERROR",
            "info": "INFO",
            "debug": "DEBUG",
            "soft_execute": "Read-only execution",
            "hard_execute": "Write execution"
        }
    }
    
    @classmethod
    def setup_logger(cls, log_file_path: str = None, language: str = "es", clear_logs: bool = False):
        """
        Setup logger with file and console handlers.
        
        Args:
            log_file_path: Path for log file. Can be:
                          - None: No logging
                          - "logs/myfile.log": Relative path from execution directory
                          - "/full/path/myfile.log": Absolute path
            language: Language for log messages ("es" or "en")
            clear_logs: If True, clears the log file content at startup
        """
        cls._language = language
        
        # If no log file path provided, don't set up logging
        if not log_file_path:
            return None
            
        if cls._logger is not None:
            return cls._logger
            
        # Handle path
        if os.path.isabs(log_file_path):
            # Absolute path
            cls._log_file_path = log_file_path
        else:
            # Relative path from current working directory
            cls._log_file_path = os.path.join(os.getcwd(), log_file_path)
        
        # Ensure log directory exists
        log_dir = os.path.dirname(cls._log_file_path)
        os.makedirs(log_dir, exist_ok=True)
        
        # Clear log file if requested
        if clear_logs and os.path.exists(cls._log_file_path):
            open(cls._log_file_path, 'w').close()
            
        # Create logger
        cls._logger = logging.getLogger('mysql_connection_pool')
        cls._logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        cls._logger.handlers.clear()
        
        # Create formatter (only for file)
        file_formatter = logging.Formatter(
            '%(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler only (no console output)
        file_handler = logging.FileHandler(cls._log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        cls._logger.addHandler(file_handler)
        
        return cls._logger
    
    @classmethod
    def get_logger(cls):
        """Get the logger instance."""
        return cls._logger
    
    @classmethod
    def _get_message(cls, key: str) -> str:
        """Get message in the configured language."""
        return cls.MESSAGES.get(cls._language, cls.MESSAGES["es"]).get(key, key)
    
    @classmethod
    def _format_log(cls, level: str, title: str, message: str = "", query: str = "", response: str = "", emoji: str = "", execution_context: str = ""):
        """Format a log entry with centered title and execution context."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create separator with centered execution context
        separator_length = 80
        separator_char = "═"
        
        # Create centered execution context line
        context_text = f"[{timestamp}] {execution_context.upper()}" if execution_context else f"[{timestamp}] SISTEMA"
        context_length = len(context_text)
        
        # Calculate padding for centering
        if context_length < separator_length:
            padding = (separator_length - context_length) // 2
            context_line = separator_char * padding + context_text + separator_char * (separator_length - padding - context_length)
        else:
            context_line = context_text
        
        log_entry = f"""
{context_line}

Action: {title}"""
        
        if message:
            log_entry += f"\n\n{message}"
        
        if query:
            log_entry += f"\n\n🔍 Query:\n\n{query}"
        
        if response:
            log_entry += f"\n\n✅ {response}"
        
        log_entry += f"\n\n{separator_char * separator_length}\n"
        
        return log_entry
    
    @classmethod
    def log_statement_execution(cls, statement_num: int, total_statements: int, query: str, success: bool = True, error_msg: str = "", rows_affected: int = 0, execution_context: str = "run_sql_file"):
        """Log SQL statement execution with SQL response details."""
        logger = cls.get_logger()
        if not logger:
            return
            
        if success:
            title = f"{cls._get_message('executing_statement')} {statement_num}/{total_statements}"
            response = f"{cls._get_message('statement_success')}:\n\n{rows_affected} row(s) affected"
        else:
            title = f"{cls._get_message('statement_error')} {statement_num}/{total_statements}"
            response = f"ERROR:\n\n{error_msg}"
        
        log_entry = cls._format_log(
            level="INFO" if success else "ERROR",
            title=title,
            query=query,
            response=response,
            execution_context=execution_context
        )
        
        if success:
            logger.info(log_entry)
        else:
            logger.error(log_entry)
    
    @classmethod
    def log_file_processing(cls, file_path: str, statement_count: int, execution_context: str = "run_sql_file"):
        """Log file processing start."""
        logger = cls.get_logger()
        if not logger:
            return
            
        title = f"{cls._get_message('processing_file')}: {os.path.basename(file_path)}"
        message = f"{cls._get_message('executing_statements')}: {statement_count}"
        
        log_entry = cls._format_log(
            level="INFO",
            title=title,
            message=message,
            execution_context=execution_context
        )
        
        logger.info(log_entry)
    
    @classmethod
    def log_files_list(cls, file_paths: List[str], execution_context: str = "run_multiple_sql_files_from_directory"):
        """Log list of files to execute."""
        logger = cls.get_logger()
        if not logger:
            return
            
        title = cls._get_message('files_to_execute')
        message = "\n".join([f"  • {path}" for path in file_paths])
        
        log_entry = cls._format_log(
            level="INFO",
            title=title,
            message=message,
            execution_context=execution_context
        )
        
        logger.info(log_entry)
    
    @classmethod
    def log_error(cls, title: str, error_msg: str, problematic_content: str = "", execution_context: str = "sistema"):
        """Log error."""
        logger = cls.get_logger()
        if not logger:
            return
            
        log_entry = cls._format_log(
            level="ERROR",
            title=title,
            message=error_msg,
            query=problematic_content if problematic_content else "",
            execution_context=execution_context
        )
        
        logger.error(log_entry)
    
    @classmethod
    def log_warning(cls, title: str, message: str = "", execution_context: str = "sistema"):
        """Log warning."""
        logger = cls.get_logger()
        if not logger:
            return
            
        log_entry = cls._format_log(
            level="WARNING",
            title=title,
            message=message,
            execution_context=execution_context
        )
        
        logger.warning(log_entry)
    
    @classmethod
    def log_operation(cls, operation_type: str, query: str, success: bool = True, error_msg: str = "", rows_affected: int = 0, execution_context: str = "operation"):
        """Log a database operation (soft or hard execute)."""
        logger = cls.get_logger()
        if not logger:
            return
            
        title = cls._get_message(operation_type)
        
        if success:
            response = f"{cls._get_message('statement_success')}:\n\n{rows_affected} row(s) affected"
        else:
            response = f"ERROR:\n\n{error_msg}"
        
        log_entry = cls._format_log(
            level="INFO" if success else "ERROR",
            title=title,
            query=query,
            response=response,
            execution_context=execution_context
        )
        
        if success:
            logger.info(log_entry)
        else:
            logger.error(log_entry)
    
    @classmethod
    def get_log_file_path(cls) -> str:
        """Get the current log file path."""
        return cls._log_file_path