from datetime import datetime
import requests
# Get the current date
current_date = datetime.now()

# Format the date as 'YYYY-MMM-DD'
formatted_date = current_date.strftime('%Y-%b-%d').upper()
oa_api_key = 'c80f14133d3748d3c465f41d78bf57e5'
# Replace the date in the URL
url = f'https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?apiKey={oa_api_key}&regions=us&dateFormat=iso&markets=spreads&oddsFormat=american'
response = requests.get(url).json()

print(response)

