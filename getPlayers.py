import requests
from datetime import datetime

api_key = 'ae9d60ebe445446e8b4cc35c45dfdfea'


# Get the current date
current_date = datetime.now()

# Format the date as 'YYYY-MMM-DD'
formatted_date = current_date.strftime('%Y-%b-%d').upper()
def fetch_mlb_players():

    url = f'https://api.sportsdata.io/v3/mlb/scores/json/Players?key={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        players = response.json()
        # Returning the list of players
        return players
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []



def get_players_propbet_hits():
    api_key = 'ae9d60ebe445446e8b4cc35c45dfdfea'
    url = f'https://api.sportsdata.io/v3/mlb/scores/json/GamesByDate/{formatted_date}={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        players = response.json()
        # Returning the list of players
        return players
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []



#def get_games_for_today():
