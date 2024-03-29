from datetime import datetime
from uuid import uuid4

from flask import Flask, request, render_template, redirect, flash, url_for
from getPlayers import *
import boto3

app = Flask(__name__)
app.secret_key = "_5#y2LF4Q8z$as!kz(9,d]/"  # Use the generated key here

session = boto3.Session(aws_access_key_id="AKIATCKANQTKSIM4LEMR", aws_secret_access_key="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")
dynamodb = session.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('pending-wagers')


@app.route('/')
def place_bet():
    mlb_players = fetch_mlb_players()
    # Render the place bet HTML page
    return render_template('place_bet.html', players=mlb_players)


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


@app.route('/pending_bets')
def pending_bets():
    try:
        response = table.scan()  # Scans the entire table, use with caution for larger datasets
        bets = response.get('Items', [])
    except Exception as e:
        print(f"Error fetching pending bets: {e}")
        bets = []

    return render_template('pending_bets.html', bets=bets)


@app.route('/bet_outcome', methods=['POST'])
def bet_outcome():
    bet_id = request.form.get('selected_bet')
    outcome = request.form.get('bet_outcome')

    try:
        if outcome == "yes":
            table.delete_item(
                Key={
                    'bet_id': bet_id
                }
            )

            ### DO MATH FOR LEADERBOARD
        elif outcome == "no":
            table.delete_item(
                Key={
                    'bet_id': bet_id
                }
            )

            ### DO MATH FOR LEADERBOARD

        response = table.scan()  # Scans the entire table, use with caution for larger datasets
        bets = response.get('Items', [])
    except Exception as e:
        print(f"Error fetching pending bets: {e}")
        bets = []  # Implement this function to get the updated bets

    # Return only the table part of the HTML
    return render_template('bet_table.html', bets=bets)


@app.route('/leaderboard')
def leaderboard():
    # Logic to calculate and display leaderboard
    # Add logic to fetch and calculate leaderboard data.
    leaderboard_data = []  # Replace with actual data
    return render_template('leaderboard.html', users=leaderboard_data)

@app.route('/test')
def testp():
    mlb_players = fetch_mlb_players()
    # Render the place bet HTML page
    return render_template('testp.html', players=mlb_players)

if __name__ == '__main__':
    app.run(debug=True)

