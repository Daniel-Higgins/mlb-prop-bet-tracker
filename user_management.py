import boto3
from boto3.dynamodb.conditions import Key
from werkzeug.security import generate_password_hash, check_password_hash
import random

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
user_table = dynamodb.Table('user-accounts')

#this file of methods helps manage users and can fix, create, maintain, and delete users


#generate user ID
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


#check if user exists
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


#get the user information
def get_user_data(em):
    response = user_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(em)
    )
    # Check if the user exists and return the first item if available
    if response['Items']:
        return response['Items'][0]  # Assuming the first item is the user data
    return None


def fix_uid_in_ht():
    # Initialize DynamoDB resource
    dynamodbf = boto3.resource('dynamodb', region_name='us-east-1')
    history_table = dynamodbf.Table('history-stats')
    user_tablef = dynamodbf.Table('user-accounts')

    # Scan the history table
    response = history_table.scan()
    history_items = response.get('Items', [])

    for item in history_items:
        bettor_username = item.get('WhoMadeTheBet')

        # Query the user table to find the user_id by username
        user_response = user_tablef.query(
            IndexName='user_name-index',  # Ensure this GSI exists in your user-accounts table
            KeyConditionExpression=Key('user_name').eq(bettor_username)
        )

        if user_response['Items']:
            user_id = user_response['Items'][0].get('user_id')

            # Update the history item with the user_id
            if user_id:
                update_response = history_table.update_item(
                    Key={'bet_id': item['bet_id']},
                    UpdateExpression="set user_id = :uid",
                    ExpressionAttributeValues={':uid': user_id},
                    ReturnValues="UPDATED_NEW"
                )
                print(f"Updated bet_id {item['bet_id']} with user_id {user_id}")
        else:
            print(f"No user found for username {bettor_username}")


def fix_password(bettor, newp):
    try:
        # First, retrieve the user by email to check old password and get user_id
        response = user_table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(bettor)
        )
        user = response['Items'][0]
        user_table.update_item(
            Key={'user_id': user['user_id']},
            UpdateExpression="SET password = :p",
            ExpressionAttributeValues={':p': generate_password_hash(newp)},
            ReturnValues="UPDATED_NEW")

    except Exception as e:
        print(e)


def delete_userpicks(username):
    # Initialize a session using Boto3
    dynamodbd = boto3.resource('dynamodb', region_name='us-east-1')
    history_table = dynamodbd.Table('history-stats')

    # Scan the table for all items where 'WhoMadeTheBet' matches the given username
    response = history_table.scan(
        FilterExpression=Key('WhoMadeTheBet').eq(username)
    )

    # Retrieve the items from the scan response
    items = response['Items']

    # Loop through the items and delete each one

    for item in items:
        print(f"Deleting item with bet_id: {item['bet_id']}")
        delete_response = history_table.delete_item(
            Key={'bet_id': item['bet_id']}
        )
        print(f"Delete response: {delete_response}")


def updateProPic(filepath, objet, uem, old_file_url=None):
    s3 = boto3.client('s3', region_name='us-east-1')
    bucket_name = "mlb-app-stuff"

    if old_file_url and not old_file_url.endswith('default-avatar.png'):
        try:
            old_key = old_file_url.split(f'https://{bucket_name}.s3.amazonaws.com/')[1]
            s3.delete_object(Bucket=bucket_name, Key=old_key)
        except Exception as e:
            return False, f"Failed to delete old profile picture: {str(e)}"

    try:
        s3.upload_fileobj(
            objet,
            bucket_name,
            filepath,
            ExtraArgs={'ContentType': objet.content_type}
        )
        # Construct the URL to the file
        file_url = f'https://{bucket_name}.s3.amazonaws.com/{filepath}'

        # Update DynamoDB with the new URL
        dynamodbpp = boto3.resource('dynamodb', region_name='us-east-1')
        user_tablepp = dynamodbpp.Table('user-accounts')

        response = user_tablepp.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(uem)
        )
        if response['Items']:
            user_id = response['Items'][0]['user_id']  # Assuming 'user_id' is the primary key
            # Now update using the primary key
            user_tablepp.update_item(
                Key={'user_id': user_id},
                UpdateExpression="set profile_pic_url = :p",
                ExpressionAttributeValues={':p': file_url}
            )
            return True, "Profile picture updated successfully!"
    except Exception as e:
        return False, str(e)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
