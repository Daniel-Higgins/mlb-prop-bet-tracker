from datetime import datetime, timedelta
import boto3
import requests
# Get the current date
from boto3.dynamodb.conditions import Key

current_date = datetime.now()
yesterday_date = current_date - timedelta(days=1)
# Format the date as 'YYYY-MMM-DD'
formatted_date = yesterday_date.strftime('%Y-%m-%d')
oa_api_key = 'c80f14133d3748d3c465f41d78bf57e5'

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
user_table = dynamodb.Table('user-accounts')


def get_games_for_today():
    url = f'https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?apiKey={oa_api_key}&regions=us&dateFormat=iso&markets=spreads&oddsFormat=american'
    response = requests.get(url).json()
    return response


