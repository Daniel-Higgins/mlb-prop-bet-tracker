from datetime import datetime, timedelta
import boto3
import requests
# Get the current date
from boto3.dynamodb.conditions import Key
from flask import flash

from leaderboard import *

current_date = datetime.now()
yesterday_date = current_date - timedelta(days=1)
# Format the date as 'YYYY-MMM-DD'
formatted_date = yesterday_date.strftime('%Y-%m-%d')

# Call the function
# fix_uid_in_ht()
