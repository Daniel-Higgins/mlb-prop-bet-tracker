from werkzeug.utils import secure_filename

from user_management import *
from uuid import uuid4
from leaderboard import do_this
from flask import Flask, request, render_template, redirect, flash, url_for, jsonify, session
from getPlayers import *
from boto3.dynamodb.conditions import Attr
import boto3

app = Flask(__name__)
app.config['VERSION_INFO'] = 'V1.3.1'
app.secret_key = "_5#y2LF4Q8z$as!kz(9,d]/"  # Use the generated key here

sessionp = boto3.Session()
dynamodb = sessionp.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('pending-wagers')


@app.route('/')
def place_bet():
    mlb_players = fetch_mlb_players()
    user_name = session.get('user_name', None)
    print(session)
    # Render the place bet HTML page
    return render_template('place_bet.html', players=mlb_players, user_name=user_name,
                           version_info=app.config['VERSION_INFO'])


@app.route('/submit_bet', methods=['POST'])
def submit_bet():
    # Check if user is logged in
    if 'user_email' not in session:
        flash('You need to log in to place a bet.', 'error')
        return redirect(url_for('login'))

    bettor_email = session['user_email']

    # Retrieve the user data from the database to ensure they are a valid user
    user_data = get_user_data(bettor_email)
    if not user_data:
        flash('Please sign in to continue.', 'error')
        return redirect(url_for('place_bet'))

    bettor_username = user_data['user_name']  # Assuming 'username' is stored in user_data
    bettor_user_id = user_data.get('user_id')

    # Check for existing pending bets for the bettor
    response = table.scan(
        FilterExpression=Attr('WhoMadeTheBet').eq(bettor_username) & Attr('Outcome').not_exists()
    )
    # Validate form data
    if not all([request.form.get('betType'), request.form.get('player'),
                request.form.get('odds'), request.form.get('book')]):
        flash('All fields are required!', 'error')
        return redirect(url_for('place_bet'))

    # Validate "Odds" value
    try:
        odds = int(request.form.get('odds'))
        if odds < -300:
            flash('Odds must be greater than -300.', 'error')
            return redirect(url_for('place_bet'))
        elif (-99 < odds < 99) or odds > 10000:
            flash('Enter valid odds.', 'error')
            return redirect(url_for('place_bet'))

        if response['Items']:
            # There's already a pending bet for this bettor
            flash('You already have a pending bet.', 'error')
            return redirect(url_for('place_bet'))

        # If validations pass, insert the bet into DynamoDB
        bet_id = str(uuid4())
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        table.put_item(
            Item={
                'bet_id': bet_id,
                'WhoMadeTheBet': bettor_username,
                'user_id': bettor_user_id,
                'TypeOfBet': request.form.get('betType'),
                'PlayerBetOn': request.form.get('player'),
                'Odds': odds,
                'Book': request.form.get('book'),
                'TimeDatePlaced': now
            }
        )
        flash('Bet placed successfully!', 'success')
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
        user_name = session.get('user_name', None)
        bets = response.get('Items', [])
    except Exception as e:
        print(f"Error fetching pending bets: {e}")
        bets = []

    return render_template('pending_bets.html', bets=bets, user_name=user_name, version_info=app.config['VERSION_INFO'])


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
    data = do_this()
    final_data = [
        {
            'bettorName': user,
            'numberOfBets': stats['numberOfBets'],
            'wins': stats['wins'],
            'losses': stats['losses'],
            'currentStreak': stats['currentStreak'],
            'longestStreak': stats['longestStreak'],
            'mostBetPlayer': stats['mostBetPlayer'],
            'avgOdds': round(stats['avgOdds'], 2) if stats['numberOfBets'] > 0 else 0,
            'mostUsedBook': stats['mostUsedBook'],
            'profilePicUrl': stats.get('profilePicUrl')
        } for user, stats in data.items()
    ]
    return jsonify(final_data)


@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard_data.html', version_info=app.config['VERSION_INFO'])


@app.route('/player_history/<player>')
def player_history(player):
    table2 = dynamodb.Table('history-stats')
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


from flask import jsonify


@app.route('/get_usernames')
def get_usernames():

    user_tablel = dynamodb.Table('user-accounts')
    response = user_tablel.scan(AttributesToGet=['user_name'])  # Make sure 'user_name' is the correct attribute key

    usernames = [item['user_name'] for item in response['Items']]

    # Handle pagination if there's a lot of data
    while 'LastEvaluatedKey' in response:
        response = user_table.scan(
            ExclusiveStartKey=response['LastEvaluatedKey'],
            AttributesToGet=['user_name']
        )
        usernames.extend([item['user_name'] for item in response['Items']])

    return jsonify(usernames)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', version_info=app.config['VERSION_INFO'])


@app.route('/contactus')
def contactus():
    return render_template('contactus.html', version_info=app.config['VERSION_INFO'])


@app.route('/games', methods=['GET'])
def games():
    try:
        b_games = get_games_for_today()  # This should now include spread and odds

    except:
        print(Exception)

    return render_template('games.html', games=b_games, version_info=app.config['VERSION_INFO'])


# to edit
@app.route('/submit_winners', methods=['POST'])
def submit_winners():
    user = session['user_name']
    dynamodbt = boto3.resource('dynamodb', region_name='us-east-1')
    tablet = dynamodbt.Table('daily-picks')
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Iterate over each game based on the submitted form data
    for key, value in request.form.items():
        if key.startswith('winner_'):
            game_id = key.split('_')[1]
            picked_winner = value
            team1 = request.form.get(f"team1_{game_id}")
            team2 = request.form.get(f"team2_{game_id}")
            matchup = f"{team1} vs {team2}"

            # Fetching odds and points for the picked team
            odds = request.form.get(f"{picked_winner}_odds")
            point = request.form.get(f"{picked_winner}_point")

            # Constructing the item to insert into the database
            item = {
                'pick_id': game_id,  # Assuming game ID is unique for each game
                'user': user,
                'date': today_date,
                'matchup': matchup,
                'picked_winner': picked_winner,
                'spread': point,
                'odds': odds,
                'outcome': 'pending'  # Default outcome, to be updated later
            }

            # Inserting the item into the DynamoDB table
            tablet.put_item(Item=item)

    return redirect(url_for('view_picks'))


@app.route('/view_picks', methods=['GET'])
def view_picks():
    return render_template('view_picks.html', version_info=app.config['VERSION_INFO'])


@app.route('/account', methods=['GET'])
def account_page():
    if 'user_email' in session:
        # Assume we store user's email in session when they log in
        user_email = session['user_email']
        print(session)
        user_data = get_user_data(user_email)
        return render_template('uprofile.html', user_data=user_data, version_info=app.config['VERSION_INFO'])
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = login_user(email, password)

        if isinstance(user, str):  # Check if the return value is an error message string
            flash(user)  # Send the error message to the next request
            return render_template('login.html')  # Render the same login page
        else:
            # Set both email and username in the session
            session['user_email'] = user['email']
            session['user_name'] = user['user_name']  # Make sure this key matches your user data structure
            return redirect(url_for('account_page'))

    return render_template('login.html', version_info=app.config['VERSION_INFO'])


@app.route('/sign_up', methods=['GET'])
def sign_up():
    return render_template('signup.html', version_info=app.config['VERSION_INFO'])


# for actual submit on signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Extract form data
        user_name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        favorite_sportsbook = request.form.get('book')
        print(user_name)

        # Validate input (you might want to add more validation logic)
        if not all([user_name, email, password, confirm_password]):
            flash('Please fill out all fields')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('signup.html')

        if len(password) < 4 or len(password) > 20:
            flash('Password must be between 6 and 20 characters')
            return render_template('signup.html')

        # Attempt to create a new user
        data = {
            'user_name': user_name,
            'email': email,
            'password': password,
            'favorite_sportsbook': favorite_sportsbook
        }
        create_user_result = create_user(data)

        if create_user_result == "User created successfully":
            flash('User created successfully. Please log in.')
            return redirect(url_for('login'))
        else:
            flash(create_user_result)  # "User already exists" or any other error
            return render_template('signup.html')

    return render_template('uprofile.html', version_info=app.config['VERSION_INFO'])


@app.route('/uprofile', methods=['GET'])
def uprofile():
    if 'user_email' in session:
        user_email = session['user_email']
        user_data = get_user_data(user_email)  # Get user data from DynamoDB

        if not user_data:
            flash("User not found. Please log in again.", "error")
            return redirect(url_for('login'))

        return render_template('uprofile.html', user_data=user_data, version_info=app.config['VERSION_INFO'])
    else:
        flash("Please log in to view this page.", "error")
        return redirect(url_for('login', version_info=app.config['VERSION_INFO']))


@app.route('/chp', methods=['POST'])
def change_password():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if new_password != confirm_new_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('account_page'))

    if len(new_password) < 4 or len(new_password) > 20:
        flash('Password must be between 4 and 20 characters.', 'error')
        return redirect(url_for('account_page'))

    user_email = session.get('user_email')
    if not user_email:
        flash('No user logged in.', 'error')
        return redirect(url_for('login'))

    # Get DynamoDB resource
    dynamodbu = boto3.resource('dynamodb', region_name='us-east-1')
    user_tableu = dynamodbu.Table('user-accounts')

    try:
        # First, retrieve the user by email to check old password and get user_id
        response = user_table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(user_email)
        )
        if not response['Items']:
            flash('User not found.', 'error')
            return redirect(url_for('account_page'))

        user = response['Items'][0]
        if not check_password_hash(user['password'], old_password):
            flash('Old password is incorrect.', 'error')
            return redirect(url_for('account_page'))

        # Update password using the primary key (user_id)
        user_tableu.update_item(
            Key={'user_id': user['user_id']},
            UpdateExpression="SET password = :p",
            ExpressionAttributeValues={':p': generate_password_hash(new_password)},
            ReturnValues="UPDATED_NEW"
        )
        flash('Password updated successfully.', 'success')
    except Exception as e:
        flash(str(e), 'error')

    return redirect(url_for('account_page'))


@app.route('/signout')
def signout():
    session.clear()  # This clears all data in the session
    return redirect(url_for('login'))  # Redirect to the login page or another appropriate page


@app.route('/update_profile_picture', methods=['POST'])
def update_profile_picture():
    if 'user_email' not in session:
        flash('You need to log in to update your profile picture.', 'error')
        return redirect(url_for('login'))

    if 'profile_picture' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('account_page'))

    file = request.files['profile_picture']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('account_page'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        s3 = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'mlb-app-stuff'

        # Create a unique S3 key
        file_key = f"user-stuff/avatar/{session['user_email']}/{filename}"

        try:
            s3.upload_fileobj(
                file,
                bucket_name,
                file_key,
                ExtraArgs={'ACL': 'public-read', 'ContentType': file.content_type}
            )

            # Store the URL or key in DynamoDB
            user_tablepp = boto3.resource('dynamodb', region_name='us-east-1').Table('user-accounts')
            user_tablepp.update_item(
                Key={'email': session['user_email']},
                UpdateExpression="set profile_picture = :p",
                ExpressionAttributeValues={
                    ':p': f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
                }
            )
            flash('Profile picture updated successfully.', 'success')
        except Exception as e:
            print(e)
            flash('Failed to upload image.', 'error')

        return redirect(url_for('account_page'))
    else:
        flash('Invalid file type.', 'error')
        return redirect(url_for('account_page'))


@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'user_email' not in session:
        flash("You must be logged in to update your profile picture.", "error")
        return redirect(url_for('login'))

    file = request.files.get('profile_pic')
    user_data = get_user_data(session['user_email'])

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_key = f"user-stuff/avatar/{session['user_email']}/{filename}"
        old_file_url = user_data.get('profile_pic_url') if user_data else None

        success, message = updateProPic(file_key, file, session['user_email'], old_file_url)

        if success:
            flash(message, "success")
        else:
            flash(message, "error")
    else:
        flash("Invalid file type. Please upload an image.", "error")

    return redirect(url_for('uprofile'))


if __name__ == '__main__':
    app.run(debug=True)
