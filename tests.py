from datetime import datetime
import requests
# Get the current date
current_date = datetime.now()

# Format the date as 'YYYY-MMM-DD'
formatted_date = current_date.strftime('%Y-%b-%d').upper()

# Replace the date in the URL
url = f"https://api.sportsdata.io/v3/mlb/scores/json/GamesByDate/{formatted_date}?key=ae9d60ebe445446e8b4cc35c45dfdfea"
response = requests.get(url).json()

