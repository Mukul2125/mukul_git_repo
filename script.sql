--i want second highest salary from employee table by analythic function
SELECT employee_id, first_name, last_name, salary,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS salary_rank
FROM employees
WHERE salary_rank = 2;