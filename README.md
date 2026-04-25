# Oracle 23ai REST API Integration

This project provides a complete REST API integration with Oracle 23ai database, including stored procedures and database utilities.

## Project Structure

```
d:\Mukul_git_repo\
├── app.py                      # Flask REST API application
├── oracle_connection.py        # Oracle database connection utilities
├── oracle_integration.py      # API integration module
├── oracle_schema.sql          # Database schema (tables, sequences)
├── oracle_procedures.sql      # Stored procedures
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Prerequisites

1. **Oracle Database 23ai** - Ensure Oracle 23ai is installed and running
2. **Python 3.8+** - Python runtime
3. **Oracle Instant Client** - Oracle client libraries

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Set the following environment variables:

```bash
export ORACLE_USER=your_username
export ORACLE_PASSWORD=your_password
export ORACLE_DSN=localhost:1521/freepdb1
```

Or create a `.env` file:

```
ORACLE_USER=system
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/freepdb1
PORT=5000
```

### 3. Set Up Oracle Database

Run the SQL scripts in Oracle 23ai:

1. First, run the schema:
```sql
@oracle_schema.sql
```

2. Then, run the procedures:
```sql
@oracle_procedures.sql
```

### 4. Start the API Server

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root information |
| GET | `/health` | Health check endpoint |
| GET | `/api/employees` | Get all employees |
| GET | `/api/employees/<id>` | Get employee by ID |
| POST | `/api/employees` | Create new employee |
| PUT | `/api/employees/<id>` | Update employee |
| DELETE | `/api/employees/<id>` | Delete employee |
| GET | `/api/employees/search?q=<term>` | Search employees |
| POST | `/api/procedures/execute` | Execute stored procedure |
| GET | `/api/audit/logs` | Get API audit logs |

## Example API Usage

### Health Check
```bash
curl http://localhost:5000/health
```

### Get All Employees
```bash
curl http://localhost:5000/api/employees
```

### Create Employee
```bash
curl -X POST http://localhost:5000/api/employees \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "department": "IT",
    "salary": 75000
  }'
```

### Update Employee
```bash
curl -X PUT http://localhost:5000/api/employees/1 \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "department": "Engineering",
    "salary": 85000
  }'
```

### Search Employees
```bash
curl "http://localhost:5000/api/employees/search?q=IT"
```

### Execute Stored Procedure
```bash
curl -X POST http://localhost:5000/api/procedures/execute \
  -H "Content-Type: application/json" \
  -d '{
    "procedure_name": "manage_employee",
    "parameters": {
      "1": 0,
      "2": "Jane",
      "3": "Doe",
      "4": "jane.doe@example.com",
      "5": "HR",
      "6": 65000
    }
  }'
```

## Stored Procedures

| Procedure | Description |
|-----------|-------------|
| `manage_employee` | Insert or update employee |
| `get_employee` | Get employee by ID |
| `delete_employee` | Delete employee by ID |
| `log_api_request` | Log API request to audit table |
| `get_all_employees` | Get all employees (function) |
| `search_employees` | Search employees (function) |

## Using the Integration Module

```python
from oracle_integration import Oracle23AIIntegration

# Initialize
api = Oracle23AIIntegration(
    api_base_url='http://localhost:5000',
    username='system',
    password='password'
)

# Get employees
result = api.get_all_employees()

# Create employee
result = api.create_employee({
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'department': 'IT',
    'salary': 75000
})
```

## Using the Connection Utility

```python
from oracle_connection import get_connection, execute_query, test_connection

# Test connection
result = test_connection()
print(result)

# Execute query
results = execute_query("SELECT * FROM employees FETCH FIRST 10 ROWS ONLY")

# Using context manager
with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees")
    # ...
```

## Troubleshooting

### Connection Issues
- Verify Oracle 23ai is running
- Check connection string (DSN)
- Ensure correct username and password

### Import Errors
- Install required packages: `pip install -r requirements.txt`
- Ensure Oracle Instant Client is installed

### Permission Errors
- Grant necessary permissions to database user
- Check Oracle roles and privileges

## License

This project is for demonstration purposes.