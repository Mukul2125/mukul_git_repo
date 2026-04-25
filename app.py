# Oracle 23ai REST API
# Flask application to integrate with Oracle 23ai database

from flask import Flask, request, jsonify
from flask_cors import CORS
import oracledb
import os
import json
from datetime import datetime
from functools import wraps

app = Flask(__name__)
CORS(app)

# Oracle Database Configuration
DB_CONFIG = {
    'user': os.environ.get('ORACLE_USER', 'system'),
    'password': os.environ.get('ORACLE_PASSWORD', 'password'),
    'dsn': os.environ.get('ORACLE_DSN', 'localhost:1521/freepdb1')
}

def get_db_connection():
    """Get Oracle database connection"""
    try:
        conn = oracledb.connect(**DB_CONFIG)
        return conn
    except oracledb.Error as e:
        print(f"Database connection error: {e}")
        raise

def log_api_call(func):
    """Decorator to log API calls"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            print(f"{func.__name__} executed in {duration:.2f}ms")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000
            print(f"{func.__name__} failed after {duration:.2f}ms: {str(e)}")
            raise
    return wrapper

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'message': 'Oracle 23ai REST API',
        'version': '1.0.0',
        'endpoints': [
            '/api/employees',
            '/api/employees/<id>',
            '/api/employees/search',
            '/api/procedures/execute',
            '/health'
        ]
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/employees', methods=['GET'])
@log_api_call
def get_employees():
    """Get all employees"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT employee_id, first_name, last_name, email, department, salary, hire_date
            FROM employees
            ORDER BY employee_id
        """)
        
        columns = [col[0] for col in cursor.description]
        employees = []
        
        for row in cursor.fetchall():
            emp = dict(zip(columns, row))
            if emp.get('hire_date'):
                emp['hire_date'] = emp['hire_date'].isoformat() if hasattr(emp['hire_date'], 'isoformat') else str(emp['hire_date'])
            employees.append(emp)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(employees),
            'data': employees
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
@log_api_call
def get_employee(employee_id):
    """Get employee by ID"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT employee_id, first_name, last_name, email, department, salary, hire_date
            FROM employees
            WHERE employee_id = :1
        """, (employee_id,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            columns = ['employee_id', 'first_name', 'last_name', 'email', 'department', 'salary', 'hire_date']
            employee = dict(zip(columns, row))
            if employee.get('hire_date'):
                employee['hire_date'] = employee['hire_date'].isoformat() if hasattr(employee['hire_date'], 'isoformat') else str(employee['hire_date'])
            
            return jsonify({
                'success': True,
                'data': employee
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Employee not found'
            }), 404
            
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees', methods=['POST'])
@log_api_call
def create_employee():
    """Create new employee"""
    conn = None
    try:
        data = request.get_json()
        
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO employees (first_name, last_name, email, department, salary)
            VALUES (:1, :2, :3, :4, :5)
            RETURNING employee_id INTO :6
        """, (
            data['first_name'],
            data['last_name'],
            data['email'],
            data.get('department'),
            data.get('salary'),
            cursor.var(oracledb.NUMBER)
        ))
        
        employee_id = cursor.var(oracledb.NUMBER).getvalue()
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Employee created successfully',
            'employee_id': employee_id
        }), 201
        
    except oracledb.IntegrityError as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': 'Email already exists'
        }), 409
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
@log_api_call
def update_employee(employee_id):
    """Update employee"""
    conn = None
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        for field in ['first_name', 'last_name', 'email', 'department', 'salary']:
            if field in data:
                update_fields.append(f"{field} = :{len(values)+1}")
                values.append(data[field])
        
        if not update_fields:
            return jsonify({
                'success': False,
                'error': 'No fields to update'
            }), 400
        
        values.append(employee_id)
        
        query = f"""
            UPDATE employees 
            SET {', '.join(update_fields)}, updated_at = SYSDATE
            WHERE employee_id = :{len(values)}
        """
        
        cursor.execute(query, values)
        conn.commit()
        
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            return jsonify({
                'success': True,
                'message': 'Employee updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Employee not found'
            }), 404
            
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
@log_api_call
def delete_employee(employee_id):
    """Delete employee"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM employees WHERE employee_id = :1", (employee_id,))
        conn.commit()
        
        rows_affected = cursor.rowcount
        cursor.close()
        conn.close()
        
        if rows_affected > 0:
            return jsonify({
                'success': True,
                'message': 'Employee deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Employee not found'
            }), 404
            
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees/search', methods=['GET'])
@log_api_call
def search_employees():
    """Search employees"""
    search_term = request.args.get('q', '')
    
    if not search_term:
        return jsonify({
            'success': False,
            'error': 'Search term is required'
        }), 400
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT employee_id, first_name, last_name, email, department, salary, hire_date
            FROM employees
            WHERE UPPER(first_name) LIKE :1
               OR UPPER(last_name) LIKE :1
               OR UPPER(email) LIKE :1
               OR UPPER(department) LIKE :1
            ORDER BY employee_id
        """, (f'%{search_term.upper()}%',))
        
        columns = [col[0] for col in cursor.description]
        employees = []
        
        for row in cursor.fetchall():
            emp = dict(zip(columns, row))
            if emp.get('hire_date'):
                emp['hire_date'] = emp['hire_date'].isoformat() if hasattr(emp['hire_date'], 'isoformat') else str(emp['hire_date'])
            employees.append(emp)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(employees),
            'data': employees
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/procedures/execute', methods=['POST'])
@log_api_call
def execute_procedure():
    """Execute stored procedure"""
    conn = None
    try:
        data = request.get_json()
        
        procedure_name = data.get('procedure_name')
        parameters = data.get('parameters', {})
        
        if not procedure_name:
            return jsonify({
                'success': False,
                'error': 'Procedure name is required'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build parameter list
        param_names = list(parameters.keys())
        param_values = list(parameters.values())
        
        # Execute procedure
        if param_names:
            placeholders = [':' + str(i+1) for i in range(len(param_names))]
            query = f"BEGIN {procedure_name}({', '.join(placeholders)}); END;"
            cursor.execute(query, param_values)
        else:
            query = f"BEGIN {procedure_name}; END;"
            cursor.execute(query)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Procedure {procedure_name} executed successfully'
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audit/logs', methods=['GET'])
@log_api_call
def get_audit_logs():
    """Get API audit logs"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        limit = request.args.get('limit', 100, type=int)
        
        cursor.execute("""
            SELECT log_id, endpoint, method, status_code, execution_time_ms, created_at
            FROM api_audit_log
            ORDER BY created_at DESC
            FETCH FIRST :1 ROWS ONLY
        """, (limit,))
        
        columns = [col[0] for col in cursor.description]
        logs = []
        
        for row in cursor.fetchall():
            log = dict(zip(columns, row))
            if log.get('created_at'):
                log['created_at'] = log['created_at'].isoformat() if hasattr(log['created_at'], 'isoformat') else str(log['created_at'])
            logs.append(log)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'data': logs
        })
        
    except Exception as e:
        if conn:
            conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)