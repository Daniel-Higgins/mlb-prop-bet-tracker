from collections import defaultdict
import boto3
from operator import itemgetter
from boto3.dynamodb.conditions import Key

session = boto3.Session()

#populate the leaderboard upon request
def do_this():
    dynamodb = session.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('history-stats')
    user_table = dynamodb.Table('user-accounts')

    response = table.scan()
    # Ensure items are sorted by 'TimeDatePlaced' in ascending order
    items = sorted(response['Items'], key=itemgetter('TimeDatePlaced'))

    leaderboard_data = defaultdict(lambda: {
        'numberOfBets': 0,
        'wins': 0,
        'losses': 0,
        'winPercentage': 0,
        'mostBetPlayer': defaultdict(int),
        'totalOdds': 0,
        'mostUsedBook': defaultdict(int),
        'betHistory': [],
        'profilePicUrl': None
    })

    usernames = set(item['WhoMadeTheBet'] for item in items)

    # Fetch profile picture URLs for all users
    for username in usernames:
        user_response = user_table.query(
            IndexName='user_name-index',  # Make sure this GSI is properly configured
            KeyConditionExpression=Key('user_name').eq(username)
        )
        if user_response['Items']:
            profile_pic_url = user_response['Items'][0].get('profile_pic_url')
            #check
            if not profile_pic_url:
                profile_pic_url = 'https://mlb-app-stuff.s3.amazonaws.com/user-stuff/avatar/default-avatar.png'

            leaderboard_data[username]['profilePicUrl'] = profile_pic_url

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
        data['winPercentage'] = (data['wins'] / data['numberOfBets'] * 100) if data['numberOfBets'] > 0 else 0
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
    for bet in bets:
        if bet == 'yes':
            current_streak += 1
        else:
            current_streak = 0
        longest_streak = max(longest_streak, current_streak)
    return current_streak, longest_streak


def fix_uid_in_ht():
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    history_table = dynamodb.Table('history-stats')
    user_table = dynamodb.Table('user-accounts')

    # Scan the history table
    response = history_table.scan()
    history_items = response.get('Items', [])

    for item in history_items:
        bettor_username = item.get('WhoMadeTheBet')

        # Query the user table to find the user_id
        user_response = user_table.query(
            IndexName='username-index',  # Ensure this GSI exists in your user-accounts table
            KeyConditionExpression=Key('user_name').eq(bettor_username)
        )

        user_id = user_response['Items'][0].get('user_id') if user_response['Items'] else None

        if user_id:
            # Update the history item with the user_id
            update_response = history_table.update_item(
                Key={'bet_id': item['bet_id']},
                UpdateExpression="set user_id = :uid",
                ExpressionAttributeValues={':uid': user_id},
                ReturnValues="UPDATED_NEW"
            )
            print(f"Updated bet_id {item['bet_id']} with user_id {user_id}")

#get bet data by user
def get_bet_data(user_name):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    history_table = dynamodb.Table('history-stats')
    user_table = dynamodb.Table('user-accounts')

    # Query the user's betting history
    response = history_table.scan(
        FilterExpression=Key('WhoMadeTheBet').eq(user_name)
    )
    bets = response.get('Items', [])

    # Sort the bets by 'TimeDatePlaced' in ascending order
    sorted_bets = sorted(bets, key=lambda x: x['TimeDatePlaced'])

    user_data = {}
    if sorted_bets:
        # Initialize user data storage
        user_data = {
            'numberOfBets': len(sorted_bets),
            'wins': sum(1 for bet in sorted_bets if bet['Outcome'] == 'yes'),
            'losses': sum(1 for bet in sorted_bets if bet['Outcome'] == 'no'),
            'winPercentage': 0,
            'mostBetPlayer': defaultdict(int),
            'totalOdds': sum(float(bet['Odds']) for bet in sorted_bets),
            'mostUsedBook': defaultdict(int),
            'betHistory': sorted_bets
        }

        for bet in sorted_bets:
            user_data['mostBetPlayer'][bet['PlayerBetOn']] += 1
            user_data['mostUsedBook'][bet['Book']] += 1

        user_data['winPercentage'] = round((user_data['wins'] / user_data['numberOfBets'] * 100) if user_data['numberOfBets'] > 0 else 0,1)
        user_data['avgOdds'] = round(user_data['totalOdds'] / user_data['numberOfBets'] if user_data['numberOfBets'] > 0 else 0,1)
        user_data['mostBetPlayer'] = max(user_data['mostBetPlayer'], key=user_data['mostBetPlayer'].get, default='N/A')
        user_data['mostUsedBook'] = max(user_data['mostUsedBook'], key=user_data['mostUsedBook'].get, default='N/A')

        # Get profile picture URL from user accounts table
        user_response = user_table.query(
            IndexName='user_name-index',
            KeyConditionExpression=Key('user_name').eq(user_name)
        )
        if user_response['Items']:
            profile_pic_url = user_response['Items'][0].get('profile_pic_url', 'https://mlb-app-stuff.s3.amazonaws.com/user-stuff/avatar/default-avatar.png')
            user_data['profilePicUrl'] = profile_pic_url

    print(user_data)

    return user_data

#get stats of last 10 bets
def get_last_10_bet_data(user_name):
    import boto3
    from collections import defaultdict
    from boto3.dynamodb.conditions import Key

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    history_table = dynamodb.Table('history-stats')
    user_table = dynamodb.Table('user-accounts')

    # Query the user's betting history
    response = history_table.scan(
        FilterExpression=Key('WhoMadeTheBet').eq(user_name)
    )
    bets = response.get('Items', [])

    # Sort the bets by 'TimeDatePlaced' in descending order and take the last 10
    sorted_bets = sorted(bets, key=lambda x: x['TimeDatePlaced'], reverse=True)[:10]

    user_data = {}
    if sorted_bets:
        # Initialize user data storage
        user_data = {
            'numberOfBets': len(sorted_bets),
            'wins': sum(1 for bet in sorted_bets if bet['Outcome'] == 'yes'),
            'losses': sum(1 for bet in sorted_bets if bet['Outcome'] == 'no'),
            'winPercentage': 0,
            'mostBetPlayer': defaultdict(int),
            'totalOdds': sum(float(bet['Odds']) for bet in sorted_bets),
            'mostUsedBook': defaultdict(int),
            'betHistory': sorted_bets,
            'last10Bets': sorted_bets,  # Record of the last 10 bets
            'avgOddsOfWinningBets': 0  # Average odds of winning bets
        }

        for bet in sorted_bets:
            user_data['mostBetPlayer'][bet['PlayerBetOn']] += 1
            user_data['mostUsedBook'][bet['Book']] += 1

        winning_bets = [float(bet['Odds']) for bet in sorted_bets if bet['Outcome'] == 'yes']
        user_data['winPercentage'] = round((user_data['wins'] / user_data['numberOfBets'] * 100) if user_data['numberOfBets'] > 0 else 0, 1)
        user_data['avgOdds'] = round(user_data['totalOdds'] / user_data['numberOfBets'] if user_data['numberOfBets'] > 0 else 0, 1)
        user_data['avgOddsOfWinningBets'] = round(sum(winning_bets) / len(winning_bets) if winning_bets else 0, 1)
        user_data['mostBetPlayer'] = max(user_data['mostBetPlayer'], key=user_data['mostBetPlayer'].get, default='N/A')
        user_data['mostUsedBook'] = max(user_data['mostUsedBook'], key=user_data['mostUsedBook'].get, default='N/A')

        # Get profile picture URL from user accounts table
        user_response = user_table.query(
            IndexName='user_name-index',
            KeyConditionExpression=Key('user_name').eq(user_name)
        )
        if user_response['Items']:
            profile_pic_url = user_response['Items'][0].get('profile_pic_url', 'https://mlb-app-stuff.s3.amazonaws.com/user-stuff/avatar/default-avatar.png')
            user_data['profilePicUrl'] = profile_pic_url

    print(user_data)

    return user_data


