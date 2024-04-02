from collections import defaultdict
import boto3

session = boto3.Session()


def do_this():
    # Initialize a DynamoDB service resource.
    dynamodb = session.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('history-stats')

    response = table.scan()
    items = response['Items']

    # Initialize a dictionary to hold the aggregated data.
    leaderboard_data = defaultdict(lambda: {
        'numberOfBets': 0,
        'wins': 0,
        'losses': 0,
        'mostBetPlayer': defaultdict(int),
        'totalOdds': 0,
        'mostUsedBook': defaultdict(int),
        'betHistory': []  # Store the bet history to calculate the win streak later
    })

    # Aggregate the data.
    for item in items:
        user = item['WhoMadeTheBet']
        leaderboard_data[user]['numberOfBets'] += 1
        leaderboard_data[user]['wins'] += item['Outcome'] == 'yes'
        leaderboard_data[user]['losses'] += item['Outcome'] == 'no'
        leaderboard_data[user]['mostBetPlayer'][item['PlayerBetOn']] += 1
        leaderboard_data[user]['totalOdds'] += float(item['Odds'])
        leaderboard_data[user]['mostUsedBook'][item['Book']] += 1
        leaderboard_data[user]['betHistory'].append(item['Outcome'])  # Append the outcome to the bet history

    # Post-process to finalize calculations.
    for user, data in leaderboard_data.items():
        data['avgOdds'] = data['totalOdds'] / data['numberOfBets']
        data['mostBetPlayer'] = max(data['mostBetPlayer'], key=data['mostBetPlayer'].get)
        data['mostUsedBook'] = max(data['mostUsedBook'], key=data['mostUsedBook'].get)
        data['winStreak'] = calculate_streak(data['betHistory'])  # Calculate the win streak

        # Remove the betHistory from the final data as it's no longer needed
        del data['betHistory']

    return leaderboard_data


def calculate_streak(bets):
    streak = 0
    for bet in reversed(bets):  # Start from the most recent bet
        if bet == 'yes':  # Increment streak if the outcome is a win
            streak += 1
        else:
            break  # Stop counting at the first loss encountered
    return streak
