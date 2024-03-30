from collections import defaultdict
import boto3

session = boto3.Session(aws_access_key_id="AKIATCKANQTKSIM4LEMR",
                        aws_secret_access_key="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")


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
        'mostUsedBook': defaultdict(int)
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

    # Post-process to finalize calculations.
    for user, data in leaderboard_data.items():
        data['avgOdds'] = data['totalOdds'] / data['numberOfBets']
        data['mostBetPlayer'] = max(data['mostBetPlayer'], key=data['mostBetPlayer'].get)
        data['mostUsedBook'] = max(data['mostUsedBook'], key=data['mostUsedBook'].get)

    return leaderboard_data
