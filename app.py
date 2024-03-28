from flask import Flask, request, render_template, redirect, flash, url_for
import boto3
from boto3.dynamodb.conditions import Key

app = Flask(__name__)
app.secret_key = "_5#y2LF4Q8z$as!kz(9,d]/"  # Use the generated key here

dynamodb = boto3.resource('dynamodb')


@app.route('/')
def place_bet():
    # Render the place bet HTML page
    return render_template('place_bet.html')


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
    except ValueError:
        flash('Invalid format for odds. Please enter a number.', 'error')
        return redirect(url_for('place_bet'))
    ##################################################### need to insert dynamo stuff here
    # Logic to insert bet into DynamoDB
    table = dynamodb.Table('Bets')
    # Insert data logic here

    # Flash a success message
    flash('Bet placed successfully!', 'success')
    # Redirect to the pending bets page
    return redirect(url_for('pending_bets'))


@app.route('/pending_bets')
def pending_bets():
    # Logic to fetch and display pending bets
    # You should add logic to fetch the pending bets from DynamoDB.
    pending_bets = []  # This should be replaced with the actual fetched bets.
    return render_template('pending_bets.html', bets=pending_bets)


@app.route('/leaderboard')
def leaderboard():
    # Logic to calculate and display leaderboard
    # Add logic to fetch and calculate leaderboard data.
    leaderboard_data = []  # Replace with actual data
    return render_template('leaderboard.html', users=leaderboard_data)


if __name__ == '__main__':
    app.run(debug=True)

