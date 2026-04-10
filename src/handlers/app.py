import json
import boto3
import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'TasksTable')
table = dynamodb.Table(table_name)


def decimal_default(obj):
    """JSON serializer for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def create_response(status_code, body):
    """Create a standardized API response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, default=decimal_default)
    }


def lambda_handler(event, context):
    """
    Main Lambda handler for Task Manager API.
    
    Endpoints:
    - GET /tasks - List all tasks
    - GET /tasks/{id} - Get a specific task
    - POST /tasks - Create a new task
    - PUT /tasks/{id} - Update a task
    - DELETE /tasks/{id} - Delete a task
    """
    print(f"Event: method={event.get('httpMethod')} path={event.get('path')}")
    
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_params = event.get('pathParameters') or {}
    
    try:
        # Handle CORS preflight
        if http_method == 'OPTIONS':
            return create_response(200, {'message': 'OK'})
        
        # Route requests
        if path == '/tasks' and http_method == 'GET':
            return get_all_tasks()
        elif path == '/tasks' and http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            return create_task(body)
        elif '/tasks/' in path and http_method == 'GET':
            task_id = path_params.get('id')
            return get_task(task_id)
        elif '/tasks/' in path and http_method == 'PUT':
            task_id = path_params.get('id')
            body = json.loads(event.get('body', '{}'))
            return update_task(task_id, body)
        elif '/tasks/' in path and http_method == 'DELETE':
            task_id = path_params.get('id')
            return delete_task(task_id)
        else:
            return create_response(404, {'error': 'Not Found'})
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        return create_response(500, {'error': str(e)})


def get_all_tasks():
    """Get all tasks from DynamoDB."""
    response = table.scan()
    tasks = response.get('Items', [])
    return create_response(200, {'tasks': tasks, 'count': len(tasks)})


def get_task(task_id):
    """Get a specific task by ID."""
    if not task_id:
        return create_response(400, {'error': 'Task ID is required'})
    
    response = table.get_item(Key={'id': task_id})
    task = response.get('Item')
    
    if not task:
        return create_response(404, {'error': 'Task not found'})
    
    return create_response(200, task)


def create_task(body):
    """Create a new task."""
    if not body.get('title'):
        return create_response(400, {'error': 'Title is required'})
    
    task = {
        'id': str(uuid.uuid4()),
        'title': body['title'],
        'description': body.get('description', ''),
        'status': body.get('status', 'pending'),
        'priority': body.get('priority', 'medium'),
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat()
    }
    
    table.put_item(Item=task)
    return create_response(201, {'message': 'Task created', 'task': task})


def update_task(task_id, body):
    """Update an existing task."""
    if not task_id:
        return create_response(400, {'error': 'Task ID is required'})
    
    # Check if task exists
    response = table.get_item(Key={'id': task_id})
    if not response.get('Item'):
        return create_response(404, {'error': 'Task not found'})
    
    # Build update expression
    update_expr = 'SET updated_at = :updated_at'
    expr_values = {':updated_at': datetime.now(timezone.utc).isoformat()}
    
    if 'title' in body:
        update_expr += ', title = :title'
        expr_values[':title'] = body['title']
    if 'description' in body:
        update_expr += ', description = :description'
        expr_values[':description'] = body['description']
    if 'status' in body:
        update_expr += ', #status = :status'
        expr_values[':status'] = body['status']
    if 'priority' in body:
        update_expr += ', priority = :priority'
        expr_values[':priority'] = body['priority']
    
    # Handle reserved keyword 'status'
    expr_names = {'#status': 'status'} if 'status' in body else None
    
    update_params = {
        'Key': {'id': task_id},
        'UpdateExpression': update_expr,
        'ExpressionAttributeValues': expr_values,
        'ReturnValues': 'ALL_NEW'
    }
    if expr_names:
        update_params['ExpressionAttributeNames'] = expr_names
    
    response = table.update_item(**update_params)
    return create_response(200, {'message': 'Task updated', 'task': response['Attributes']})


def delete_task(task_id):
    """Delete a task."""
    if not task_id:
        return create_response(400, {'error': 'Task ID is required'})
    
    # Check if task exists
    response = table.get_item(Key={'id': task_id})
    if not response.get('Item'):
        return create_response(404, {'error': 'Task not found'})
    
    table.delete_item(Key={'id': task_id})
    return create_response(200, {'message': 'Task deleted', 'id': task_id})


# Health check endpoint
def health_check(event, context):
    """Health check for the API."""
    return create_response(200, {
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })
