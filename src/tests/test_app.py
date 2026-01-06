import json
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the handlers directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'handlers'))

from app import (
    lambda_handler,
    create_response,
    get_all_tasks,
    create_task,
    health_check
)


class TestCreateResponse:
    """Tests for the create_response helper function."""
    
    def test_creates_valid_response(self):
        response = create_response(200, {'message': 'success'})
        
        assert response['statusCode'] == 200
        assert 'Content-Type' in response['headers']
        assert response['headers']['Content-Type'] == 'application/json'
        assert 'Access-Control-Allow-Origin' in response['headers']
        
    def test_serializes_body_to_json(self):
        response = create_response(200, {'key': 'value'})
        body = json.loads(response['body'])
        
        assert body['key'] == 'value'


class TestLambdaHandler:
    """Tests for the main Lambda handler."""
    
    def test_options_request_returns_200(self):
        event = {'httpMethod': 'OPTIONS', 'path': '/tasks'}
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 200
    
    def test_unknown_path_returns_404(self):
        event = {'httpMethod': 'GET', 'path': '/unknown'}
        response = lambda_handler(event, None)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body


class TestCreateTask:
    """Tests for task creation."""
    
    @patch('app.table')
    def test_creates_task_with_title(self, mock_table):
        mock_table.put_item.return_value = {}
        
        body = {'title': 'Test Task', 'description': 'Test Description'}
        response = create_task(body)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['task']['title'] == 'Test Task'
        assert 'id' in body['task']
        
    def test_returns_error_without_title(self):
        body = {'description': 'No title'}
        response = create_task(body)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body


class TestGetAllTasks:
    """Tests for getting all tasks."""
    
    @patch('app.table')
    def test_returns_empty_list_when_no_tasks(self, mock_table):
        mock_table.scan.return_value = {'Items': []}
        
        response = get_all_tasks()
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['tasks'] == []
        assert body['count'] == 0
    
    @patch('app.table')
    def test_returns_tasks_when_exist(self, mock_table):
        mock_table.scan.return_value = {
            'Items': [
                {'id': '1', 'title': 'Task 1'},
                {'id': '2', 'title': 'Task 2'}
            ]
        }
        
        response = get_all_tasks()
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert len(body['tasks']) == 2
        assert body['count'] == 2


class TestHealthCheck:
    """Tests for the health check endpoint."""
    
    def test_returns_healthy_status(self):
        response = health_check({}, None)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['status'] == 'healthy'
        assert body['version'] == '1.0.0'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
