-- Oracle 23ai Database Schema
-- This script creates the necessary tables for Oracle 23ai integration

-- Create sample data table
CREATE TABLE employees (
    employee_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR2(100) NOT NULL,
    last_name VARCHAR2(100) NOT NULL,
    email VARCHAR2(255) UNIQUE NOT NULL,
    department VARCHAR2(100),
    salary NUMBER(10, 2),
    hire_date DATE DEFAULT SYSDATE,
    created_at TIMESTAMP DEFAULT SYSDATE,
    updated_at TIMESTAMP DEFAULT SYSDATE
);

-- Create audit log table
CREATE TABLE api_audit_log (
    log_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    endpoint VARCHAR2(255) NOT NULL,
    method VARCHAR2(10) NOT NULL,
    request_data CLOB,
    response_data CLOB,
    status_code NUMBER,
    execution_time_ms NUMBER,
    created_at TIMESTAMP DEFAULT SYSDATE
);

-- Create sequence for stored procedure
CREATE SEQUENCE api_seq START WITH 1 INCREMENT BY 1;

-- Comment on tables
COMMENT ON TABLE employees IS 'Employee data table for Oracle 23ai integration';
COMMENT ON TABLE api_audit_log IS 'Audit log for API requests';