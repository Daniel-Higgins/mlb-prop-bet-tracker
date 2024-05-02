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
oa_api_key = 'c80f14133d3748d3c465f41d78bf57e5'

# Call the function
# fix_uid_in_ht()
#fix_password("nickvolz1@gmail.com","idiot_face")

get_bet_data("Higgins")