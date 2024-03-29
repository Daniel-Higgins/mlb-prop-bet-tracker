import requests

def fetch_mlb_players():
    api_key = 'ae9d60ebe445446e8b4cc35c45dfdfea'
    url = f'https://api.sportsdata.io/v3/mlb/scores/json/Players?key={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        players = response.json()
        # Returning the list of players
        return players
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return []