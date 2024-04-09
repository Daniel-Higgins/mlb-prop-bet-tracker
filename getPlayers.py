import pytz
import requests
from datetime import datetime

api_key = 'ae9d60ebe445446e8b4cc35c45dfdfea'
oa_api_key = 'c80f14133d3748d3c465f41d78bf57e5'
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


def get_games_for_today():
    url = f'https://api.the-odds-api.com/v4/sports/baseball_mlb/odds?apiKey={oa_api_key}&regions=us&dateFormat=iso&markets=spreads&oddsFormat=american'
    response = requests.get(url).json()

    # Get today's date in Eastern Time
    et_timezone = pytz.timezone('US/Eastern')
    today_date = datetime.now(et_timezone).date()

    games_data = []
    for game in response:
        # Parse the game's commence time and convert it to Eastern Time
        commence_time = datetime.fromisoformat(game['commence_time'].replace('Z', '+00:00'))
        commence_time_et = commence_time.astimezone(et_timezone)

        # Only include the game if it's happening today
        if commence_time_et.date() == today_date:
            game_info = {
                'game_id': game['id'],
                'home_team': game['home_team'],
                'away_team': game['away_team'],
                'commence_time': commence_time_et.strftime('%I:%M %p'),
                'odds': {}
            }

            # Extract the odds from FanDuel bookmaker
            for bookmaker in game['bookmakers']:
                if bookmaker['key'] == 'fanduel':
                    market = bookmaker['markets'][0]
                    for outcome in market['outcomes']:
                        point = outcome['point']
                        if point > 0 and not str(point).startswith('+'):
                            point = f"+{point}"
                        game_info['odds'][outcome['name']] = {
                            'price': outcome['price'],
                            'point': point
                        }
                    break

            games_data.append(game_info)

    return games_data
