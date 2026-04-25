# Oracle 23ai Connection Utility
# Database connection and utility functions for Oracle 23ai

import oracledb
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple
import json

class OracleConnection:
    """Oracle Database connection manager"""
    
    def __init__(self, user: str = None, password: str = None, dsn: str = None):
        """
        Initialize Oracle connection
        
        Args:
            user: Oracle database username
            password: Oracle database password
            dsn: Oracle connection string (host:port/service)
        """
        self.user = user or os.environ.get('ORACLE_USER', 'system')
        self.password = password or os.environ.get('ORACLE_PASSWORD', 'password')
        self.dsn = dsn or os.environ.get('ORACLE_DSN', 'localhost:1521/freepdb1')
        self.connection = None
    
    def connect(self) -> oracledb.Connection:
        """Create and return a new database connection"""
        try:
            conn = oracledb.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            return conn
        except oracledb.Error as e:
            print(f"Connection error: {e}")
            raise
    
    def get_connection(self) -> oracledb.Connection:
        """Get existing connection or create new one"""
        if self.connection is None or not self.connection.is_connected():
            self.connection = self.connect()
        return self.connection
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


@contextmanager
def get_connection(user: str = None, password: str = None, dsn: str = None):
    """
    Context manager for Oracle database connections
    
    Usage:
        with get_connection() as conn:
            cursor = conn.cursor()
            # do something
    """
    conn = OracleConnection(user, password, dsn)
    try:
        yield conn.get_connection()
    finally:
        conn.close()


def execute_query(query: str, params: tuple = None, fetch: bool = True) -> List[Tuple]:
    """
    Execute a SQL query
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: Whether to fetch results
    
    Returns:
        List of tuples (for SELECT) or rowcount (for INSERT/UPDATE/DELETE)
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
        finally:
            cursor.close()


def execute_procedure(procedure_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a stored procedure
    
    Args:
        procedure_name: Name of the stored procedure
        params: Dictionary of parameter values
    
    Returns:
        Dictionary with results
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            if params:
                param_list = list(params.values())
                placeholders = [':' + str(i+1) for i in range(len(params))]
                query = f"BEGIN {procedure_name}({', '.join(placeholders)}); END;"
                cursor.execute(query, param_list)
            else:
                query = f"BEGIN {procedure_name}; END;"
                cursor.execute(query)
            
            conn.commit()
            return {'success': True, 'message': f'Procedure {procedure_name} executed'}
        except Exception as e:
            conn.rollback()
            return {'success': False, 'error': str(e)}
        finally:
            cursor.close()


def execute_function(function_name: str, params: Dict[str, Any] = None) -> Any:
    """
    Execute a stored function
    
    Args:
        function_name: Name of the stored function
        params: Dictionary of parameter values
    
    Returns:
        Function return value
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            if params:
                param_list = list(params.values())
                placeholders = [':' + str(i+1) for i in range(len(params))]
                query = f"SELECT {function_name}({', '.join(placeholders)}) FROM DUAL"
                cursor.execute(query, param_list)
            else:
                query = f"SELECT {function_name}() FROM DUAL"
                cursor.execute(query)
            
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()


def get_table_data(table_name: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get data from a table
    
    Args:
        table_name: Name of the table
        limit: Maximum number of rows
    
    Returns:
        List of dictionaries representing rows
    """
    query = f"SELECT * FROM {table_name} FETCH FIRST :1 ROWS ONLY"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            # Get column names
            cursor.execute(f"SELECT * FROM {table_name} WHERE ROWNUM = 1")
            columns = [col[0] for col in cursor.description]
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name} FETCH FIRST :1 ROWS ONLY", (limit,))
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        finally:
            cursor.close()


def test_connection() -> Dict[str, Any]:
    """
    Test Oracle database connection
    
    Returns:
        Dictionary with connection status
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT SYSDATE FROM DUAL")
            result = cursor.fetchone()
            cursor.close()
            
            return {
                'success': True,
                'message': 'Connection successful',
                'server_time': str(result[0]) if result else None
            }
    except Exception as e:
        return {
            'success': False,
            'message': 'Connection failed',
            'error': str(e)
        }


# Example usage
if __name__ == '__main__':
    # Test connection
    print("Testing Oracle connection...")
    result = test_connection()
    print(json.dumps(result, indent=2))