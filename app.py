from datetime import datetime
from uuid import uuid4
import pytz
from leaderboard import do_this
from flask import Flask, request, render_template, redirect, flash, url_for, jsonify
from getPlayers import *
from boto3.dynamodb.conditions import Attr
import boto3

app = Flask(__name__)
app.config['VERSION_INFO'] = 'V1.0.6'
app.secret_key = "_5#y2LF4Q8z$as!kz(9,d]/"  # Use the generated key here

session = boto3.Session(aws_access_key_id="AKIATCKANQTKSIM4LEMR", aws_secret_access_key="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")
dynamodb = session.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('pending-wagers')


@app.route('/')
def place_bet():
    mlb_players = fetch_mlb_players()
    # Render the place bet HTML page
    return render_template('place_bet.html', players=mlb_players, version_info=app.config['VERSION_INFO'])


@app.route('/submit_bet', methods=['POST'])
def submit_bet():
    # Validate form data
    if not all([request.form.get('user'), request.form.get('betType'), request.form.get('player'), request.form.get('odds'), request.form.get('book')]):
        flash('All fields are required!', 'error')
        return redirect(url_for('place_bet'))

    # Validate "Odds" value
    try:
        odds = int(request.form.get('odds'))
        if odds < -300:
            flash('Odds must be greater than -300.', 'error')
            return redirect(url_for('place_bet'))
        elif (odds > -99 and odds < 99) or odds > 10000:
            flash('Enter Valid Odds.', 'error')
            return redirect(url_for('place_bet'))

        # If validations pass, insert the bet into DynamoDB
        bet_id = str(uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        table.put_item(
            Item={
                'bet_id': bet_id,
                'WhoMadeTheBet': request.form.get('user'),
                'TypeOfBet': request.form.get('betType'),
                'PlayerBetOn': request.form.get('player'),
                'Odds': odds,  # Storing as a string for consistency
                'Book': request.form.get('book'),
                'TimeDatePlaced': now
            }
        )
        flash('Bet placed successfully!', 'success')
        # Redirect to the pending bets page
        return redirect(url_for('pending_bets'))

    except ValueError:
        flash('Invalid format for odds. Please enter a number.', 'error')
        return redirect(url_for('place_bet'))



def convert_utc_to_local(utc_time_str, user_timezone):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%d %H:%M:%S")
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    local_time = utc_time.astimezone(pytz.timezone(user_timezone))
    return local_time.strftime("%Y-%m-%d %H:%M:%S")


@app.route('/pending_bets')
def pending_bets():
    try:
        response = table.scan()  # Scans the entire table, use with caution for larger datasets
        bets = response.get('Items', [])
    except Exception as e:
        print(f"Error fetching pending bets: {e}")
        bets = []

    return render_template('pending_bets.html', bets=bets, version_info=app.config['VERSION_INFO'])


@app.route('/bet_outcome', methods=['POST'])
def bet_outcome():
    bet_id = request.form.get('selected_bet')
    outcome = request.form.get('bet_outcome')

    try:
        response = table.get_item(
            Key={
                'bet_id': bet_id
            }
        )
        bet_item = response.get('Item', {})

        if bet_item:
            # Add the outcome to the bet item
            bet_item['Outcome'] = outcome

            # Insert the bet item into the history table
            history_table = dynamodb.Table('history-stats')
            history_table.put_item(Item=bet_item)

            # Delete the bet item from the pending-wagers table
            table.delete_item(
                Key={
                    'bet_id': bet_id
                }
            )

        response = table.scan()  # Scans the entire table, use with caution for larger datasets
        bets = response.get('Items', [])
    except Exception as e:
        print(f"Error fetching pending bets: {e}")
        bets = []  # Implement this function to get the updated bets

    # Return only the table part of the HTML
    return render_template('bet_table.html', bets=bets)


@app.route('/leaderboard_data')
def leaderboard_data():

    # Convert the aggregated data to a list of dictionaries.
    final_data = [
        {
            'bettorName': user,
            'numberOfBets': data['numberOfBets'],
            'wins': data['wins'],
            'losses': data['losses'],
            'mostBetPlayer': data['mostBetPlayer'],
            'avgOdds': data['avgOdds'] if data['avgOdds'] < -99 or data['avgOdds'] > 99 else int(-100),
            'mostUsedBook': data['mostUsedBook']
        } for user, data in do_this().items()
    ]

    return jsonify(final_data)


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard_data.html', version_info=app.config['VERSION_INFO'])


@app.route('/player_history/<player>')
def player_history(player):
    table2 = dynamodb.Table('history-stats')
    # Assuming 'PlayerBetOn' is the attribute you want to filter by in your DynamoDB table
    response = table2.scan(
        FilterExpression=Attr('WhoMadeTheBet').eq(player)
    )

    bets = response['Items']

    # Transform the bets to your desired format if needed
    player_history_data = [
        {
            'datePlaced': bet.get('TimeDatePlaced', 'N/A'),
            'outcome': bet.get('Outcome', 'N/A'),
            'typeOfBet': bet.get('TypeOfBet', 'N/A'),
            'playerBetOn': bet['PlayerBetOn'],
            'odds': bet.get('Odds', 'N/A'),
            'book': bet.get('Book', 'N/A'),
        } for bet in bets
    ]

    return jsonify(player_history_data)

@app.route('/test')
def testp():
    mlb_players = fetch_mlb_players()
    # Render the place bet HTML page
    return render_template('testp.html', players=mlb_players, version_info=app.config['VERSION_INFO'])

if __name__ == '__main__':
    app.run(debug=True)

