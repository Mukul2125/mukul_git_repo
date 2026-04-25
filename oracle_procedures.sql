-- Oracle 23ai Stored Procedures
-- This script creates stored procedures for Oracle 23ai integration

-- Procedure to insert/update employee
CREATE OR REPLACE PROCEDURE manage_employee (
    p_employee_id IN NUMBER,
    p_first_name IN VARCHAR2,
    p_last_name IN VARCHAR2,
    p_email IN VARCHAR2,
    p_department IN VARCHAR2,
    p_salary IN NUMBER,
    p_action OUT VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    IF p_employee_id IS NULL OR p_employee_id = 0 THEN
        -- Insert new employee
        INSERT INTO employees (first_name, last_name, email, department, salary)
        VALUES (p_first_name, p_last_name, p_email, p_department, p_salary);
        p_action := 'INSERTED';
    ELSE
        -- Check if employee exists
        SELECT COUNT(*) INTO v_count FROM employees WHERE employee_id = p_employee_id;
        
        IF v_count > 0 THEN
            -- Update existing employee
            UPDATE employees 
            SET first_name = p_first_name,
                last_name = p_last_name,
                email = p_email,
                department = p_department,
                salary = p_salary,
                updated_at = SYSDATE
            WHERE employee_id = p_employee_id;
            p_action := 'UPDATED';
        ELSE
            -- Insert new employee with ID
            INSERT INTO employees (employee_id, first_name, last_name, email, department, salary)
            VALUES (p_employee_id, p_first_name, p_last_name, p_email, p_department, p_salary);
            p_action := 'INSERTED';
        END IF;
    END IF;
    
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_action := 'ERROR: ' || SQLERRM;
END manage_employee;
/

-- Procedure to get employee by ID
CREATE OR REPLACE PROCEDURE get_employee (
    p_employee_id IN NUMBER,
    p_first_name OUT VARCHAR2,
    p_last_name OUT VARCHAR2,
    p_email OUT VARCHAR2,
    p_department OUT VARCHAR2,
    p_salary OUT NUMBER,
    p_hire_date OUT DATE
) AS
BEGIN
    SELECT first_name, last_name, email, department, salary, hire_date
    INTO p_first_name, p_last_name, p_email, p_department, p_salary, p_hire_date
    FROM employees
    WHERE employee_id = p_employee_id;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        p_first_name := NULL;
        p_last_name := NULL;
        p_email := NULL;
        p_department := NULL;
        p_salary := NULL;
        p_hire_date := NULL;
END get_employee;
/

-- Procedure to delete employee
CREATE OR REPLACE PROCEDURE delete_employee (
    p_employee_id IN NUMBER,
    p_result OUT VARCHAR2
) AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM employees WHERE employee_id = p_employee_id;
    
    IF v_count > 0 THEN
        DELETE FROM employees WHERE employee_id = p_employee_id;
        COMMIT;
        p_result := 'SUCCESS: Employee deleted';
    ELSE
        p_result := 'ERROR: Employee not found';
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_result := 'ERROR: ' || SQLERRM;
END delete_employee;
/

-- Procedure to log API request
CREATE OR REPLACE PROCEDURE log_api_request (
    p_endpoint IN VARCHAR2,
    p_method IN VARCHAR2,
    p_request_data IN CLOB,
    p_response_data IN CLOB,
    p_status_code IN NUMBER,
    p_execution_time_ms IN NUMBER
) AS
BEGIN
    INSERT INTO api_audit_log (endpoint, method, request_data, response_data, status_code, execution_time_ms)
    VALUES (p_endpoint, p_method, p_request_data, p_response_data, p_status_code, p_execution_time_ms);
    COMMIT;
END log_api_request;
/

-- Function to get all employees
CREATE OR REPLACE FUNCTION get_all_employees RETURN SYS_REFCURSOR AS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT employee_id, first_name, last_name, email, department, salary, hire_date
        FROM employees
        ORDER BY employee_id;
    RETURN v_cursor;
END get_all_employees;
/

-- Function to search employees
CREATE OR REPLACE FUNCTION search_employees(p_search_term IN VARCHAR2) RETURN SYS_REFCURSOR AS
    v_cursor SYS_REFCURSOR;
BEGIN
    OPEN v_cursor FOR
        SELECT employee_id, first_name, last_name, email, department, salary, hire_date
        FROM employees
        WHERE UPPER(first_name) LIKE '%' || UPPER(p_search_term) || '%'
           OR UPPER(last_name) LIKE '%' || UPPER(p_search_term) || '%'
           OR UPPER(email) LIKE '%' || UPPER(p_search_term) || '%'
           OR UPPER(department) LIKE '%' || UPPER(p_search_term) || '%'
        ORDER BY employee_id;
    RETURN v_cursor;
END search_employees;
/

SHOW ERRORS;