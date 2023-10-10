from flask import Flask, render_template, request, redirect, url_for, flash
import boto3
from botocore.exceptions import NoCredentialsError
from flask_paginate import Pagination
import os

app = Flask(__name__)
DYNAMO_ACCESS_KEY_ID = os.getenv("DYNAMO_ACCESS_KEY_ID")
DYNAMO_SECRET_ACCESS_KEY = os.getenv("DYNAMO_SECRET_ACCESS_KEY")
DYNAMO_REGION = os.getenv("DYNAMO_REGION")


# Configure AWS DynamoDB client
dynamodb = boto3.resource('dynamodb',region_name='us-west-2'
, endpoint_url='http://localhost:8000')
# Define your DynamoDB table
table_name = 'EmployeeTable'
table = dynamodb.Table(table_name)

# Create the DynamoDB table if it doesn't exist
if not dynamodb.Table(table_name).table_status == 'ACTIVE':
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'N'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

@app.route('/')
def list_employees():
    employees = [
        {"id": 1, "name": "John Doe", "position": "Manager"},
        {"id": 2, "name": "Jane Smith", "position": "Developer"},
        {"id": 3, "name": "Doe Smith", "position": "Manager"},
        {"id": 4, "name": "Jhony Sam", "position": "Developer"},
        {"id": 5, "name": "Pter Pan", "position": "Manager"},
        {"id": 6, "name": "Daisy Pam", "position": "Developer"},
        {"id": 7, "name": "Patty Doe", "position": "Manager"},
        {"id": 8, "name": "Kenny Sam", "position": "Developer"},
        {"id": 9, "name": "Sheela John", "position": "Manager"},
        {"id": 10, "name": "Jane Smith", "position": "Developer"},
        {"id": 11, "name": "John Doe", "position": "Manager"},
        {"id": 12, "name": "Jane Smith", "position": "Developer"},
        {"id": 13, "name": "John Doe", "position": "Manager"},
        {"id": 14, "name": "Jane Smith", "position": "Developer"},
        {"id": 15, "name": "John Doe", "position": "Manager"},
        {"id": 16, "name": "Jane Smith", "position": "Developer"},
        {"id": 17, "name": "John Doe", "position": "Manager"},
        {"id": 18, "name": "Jane Smith", "position": "Developer"},
        {"id": 19, "name": "John Doe", "position": "Manager"},
        {"id": 20, "name": "Jane Smith", "position": "Developer"},
        {"id": 21, "name": "John Doe", "position": "Manager"},
        {"id": 22, "name": "Jane Smith", "position": "Developer"}
    ]

    try:
        response = table.scan()
        employees = response['Items']
    except NoCredentialsError:
        flash('AWS credentials not found. Check your configuration.', 'danger')
        employees = []

    # Pagination setup
    page = int(request.args.get('page', 1))
    per_page = 10
    offset = (page - 1) * per_page
    total = len(employees)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('index.html', employees=employees[offset:offset+per_page], pagination=pagination)

@app.route('/employee/create', methods=['GET', 'POST'])
def create_employee():
    if request.method == 'POST':
        try:
            id = int(request.form['id'])
            name = request.form['name']
            position = request.form['position']
            table.put_item(Item={'id': id, 'name': name, 'position': position})
            flash('Employee created successfully', 'success')
            return redirect(url_for('list_employees'))
        except ValueError:
            flash('Invalid input. ID should be an integer.', 'danger')
    return render_template('create.html')

@app.route('/employee/edit/<employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    try:
        employee = table.get_item(Key={'id': int(employee_id)})['Item']
    except (NoCredentialsError, KeyError):
        flash('AWS credentials not found or Employee not found.', 'danger')
        return redirect(url_for('list_employees'))

    if request.method == 'POST':
        try:
            name = request.form['name']
            position = request.form['position']
            table.update_item(
                Key={'id': int(employee_id)},
                UpdateExpression='SET name = :n, position = :p',
                ExpressionAttributeValues={':n': name, ':p': position}
            )
            flash('Employee updated successfully', 'success')
            return redirect(url_for('list_employees'))
        except ValueError:
            flash('Invalid input. ID should be an integer.', 'danger')

    return render_template('edit.html', employee=employee)

@app.route('/employee/delete/<employee_id>', methods=['POST'])
def delete_employee(employee_id):
    try:
        table.delete_item(Key={'id': int(employee_id)})
        flash('Employee deleted successfully', 'success')
    except (NoCredentialsError, KeyError):
        flash('AWS credentials not found or Employee not found.', 'danger')
    return redirect(url_for('list_employees'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
