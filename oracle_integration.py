# Oracle 23ai API Integration Module
# This module provides integration utilities for Oracle 23ai

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64


class Oracle23AIIntegration:
    """Integration class for Oracle 23ai"""
    
    def __init__(self, api_base_url: str, api_key: str = None, username: str = None, password: str = None):
        """
        Initialize Oracle 23ai integration
        
        Args:
            api_base_url: Base URL of the REST API
            api_key: API key for authentication
            username: Username for basic auth
            password: Password for basic auth
        """
        self.api_base_url = api_base_url.rstrip('/')
        self.session = requests.Session()
        
        # Set authentication
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
        elif username and password:
            self.session.headers.update({
                'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """
        Make HTTP request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
        
        Returns:
            Response dictionary
        """
        url = f"{self.api_base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, json=data, params=params)
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json() if response.content else None,
                'status_code': response.status_code
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None)
            }
    
    # Employee endpoints
    def get_all_employees(self, limit: int = 100) -> Dict[str, Any]:
        """Get all employees"""
        return self._make_request('GET', '/api/employees', params={'limit': limit})
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Get employee by ID"""
        return self._make_request('GET', f'/api/employees/{employee_id}')
    
    def create_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new employee"""
        return self._make_request('POST', '/api/employees', data=employee_data)
    
    def update_employee(self, employee_id: int, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update employee"""
        return self._make_request('PUT', f'/api/employees/{employee_id}', data=employee_data)
    
    def delete_employee(self, employee_id: int) -> Dict[str, Any]:
        """Delete employee"""
        return self._make_request('DELETE', f'/api/employees/{employee_id}')
    
    def search_employees(self, search_term: str) -> Dict[str, Any]:
        """Search employees"""
        return self._make_request('GET', '/api/employees/search', params={'q': search_term})
    
    # Procedure execution
    def execute_procedure(self, procedure_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute stored procedure"""
        return self._make_request('POST', '/api/procedures/execute', data={
            'procedure_name': procedure_name,
            'parameters': parameters or {}
        })
    
    # Audit logs
    def get_audit_logs(self, limit: int = 100) -> Dict[str, Any]:
        """Get API audit logs"""
        return self._make_request('GET', '/api/audit/logs', params={'limit': limit})
    
    # Health check
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._make_request('GET', '/health')


class Oracle23AISync:
    """Data synchronization class for Oracle 23ai"""
    
    def __init__(self, integration: Oracle23AIIntegration):
        self.integration = integration
    
    def sync_employee(self, employee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync employee data (create or update)
        
        Args:
            employee_data: Employee data dictionary
        
        Returns:
            Sync result
        """
        employee_id = employee_data.get('employee_id')
        
        if employee_id:
            # Update existing
            result = self.integration.update_employee(employee_id, employee_data)
            if result.get('success'):
                return {
                    'action': 'updated',
                    'employee_id': employee_id,
                    'result': result
                }
        else:
            # Create new
            result = self.integration.create_employee(employee_data)
            if result.get('success'):
                return {
                    'action': 'created',
                    'employee_id': result.get('data', {}).get('employee_id'),
                    'result': result
                }
        
        return {
            'action': 'failed',
            'employee_id': employee_id,
            'result': result
        }
    
    def bulk_sync_employees(self, employees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk sync employees
        
        Args:
            employees: List of employee data dictionaries
        
        Returns:
            Bulk sync result
        """
        results = []
        success_count = 0
        failure_count = 0
        
        for employee in employees:
            result = self.sync_employee(employee)
            if result.get('result', {}).get('success'):
                success_count += 1
            else:
                failure_count += 1
            results.append(result)
        
        return {
            'total': len(employees),
            'success': success_count,
            'failed': failure_count,
            'results': results
        }


# Example usage
if __name__ == '__main__':
    # Initialize integration
    api = Oracle23AIIntegration(
        api_base_url='http://localhost:5000',
        username='system',
        password='password'
    )
    
    # Health check
    print("Health check:")
    print(json.dumps(api.health_check(), indent=2))
    
    # Get all employees
    print("\nGet all employees:")
    print(json.dumps(api.get_all_employees(), indent=2))
    
    # Create employee
    print("\nCreate employee:")
    print(json.dumps(api.create_employee({
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'department': 'IT',
        'salary': 75000
    }), indent=2))