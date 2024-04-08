from collections import defaultdict
import boto3
from operator import itemgetter
session = boto3.Session()

def do_this():
    dynamodb = session.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('history-stats')

    response = table.scan()
    # Ensure items are sorted by 'TimeDatePlaced' in ascending order
    items = sorted(response['Items'], key=itemgetter('TimeDatePlaced'))

    leaderboard_data = defaultdict(lambda: {
        'numberOfBets': 0,
        'wins': 0,
        'losses': 0,
        'mostBetPlayer': defaultdict(int),
        'totalOdds': 0,
        'mostUsedBook': defaultdict(int),
        'betHistory': []
    })

    for item in items:
        user = item['WhoMadeTheBet']
        leaderboard_data[user]['numberOfBets'] += 1
        leaderboard_data[user]['wins'] += item['Outcome'] == 'yes'
        leaderboard_data[user]['losses'] += item['Outcome'] == 'no'
        leaderboard_data[user]['mostBetPlayer'][item['PlayerBetOn']] += 1
        leaderboard_data[user]['totalOdds'] += float(item['Odds'])
        leaderboard_data[user]['mostUsedBook'][item['Book']] += 1
        leaderboard_data[user]['betHistory'].append(item['Outcome'])

    for user, data in leaderboard_data.items():
        data['avgOdds'] = data['totalOdds'] / data['numberOfBets'] if data['numberOfBets'] else 0
        data['mostBetPlayer'] = max(data['mostBetPlayer'], key=data['mostBetPlayer'].get, default='N/A')
        data['mostUsedBook'] = max(data['mostUsedBook'], key=data['mostUsedBook'].get, default='N/A')
        current_streak, longest_streak = calculate_streaks(data['betHistory'])
        data['currentStreak'] = current_streak
        data['longestStreak'] = longest_streak
        del data['betHistory']

    return leaderboard_data


def calculate_streaks(bets):
    current_streak = 0
    longest_streak = 0
    for bet in reversed(bets):
        if bet == 'yes':
            current_streak += 1
        else:
            current_streak = 0
        longest_streak = max(longest_streak, current_streak)
    return current_streak, longest_streak
