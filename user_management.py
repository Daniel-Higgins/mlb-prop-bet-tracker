import boto3
from boto3.dynamodb.conditions import Key
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
import random

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
user_table = dynamodb.Table('user-accounts')


def generate_unique_user_id():
    while True:
        user_id = str(random.randint(100, 9999999))  # Example range for user ID
        response = user_table.get_item(Key={'user_id': user_id})
        if 'Item' not in response:
            return user_id


def create_user(data):
    email = data.get('email')
    if check_user(email):
        return "User already exists."

    user_id = generate_unique_user_id()
    hashed_password = generate_password_hash(data.get('password'))

    item = {
        'user_id': user_id,
        'email': email,
        'user_name': data.get('user_name'),
        'password': hashed_password,
        'favorite_sportsbook': data.get('favorite_sportsbook')
    }

    user_table.put_item(Item=item)
    return "User created successfully"


def check_user(email):
    # Assuming 'email-index' is the name of the GSI on the 'email' attribute
    response = user_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )
    return bool(response['Items'])  # Returns True if user exists, False otherwise


def login_user(email, password):
    # Use the GSI to query by email
    response = user_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )

    # Check if the user exists
    if not response['Items']:
        return "User does not exist."

    user = response['Items'][0]  # Assuming the first item is the user

    # Verify the password
    if not check_password_hash(user['password'], password):
        return "Password is incorrect."

    # User authentication successful
    return user  # Return user data or a success message


def get_user_data(em):
    response = user_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(em)
    )
    # Check if the user exists and return the first item if available
    if response['Items']:
        return response['Items'][0]  # Assuming the first item is the user data
    return None
