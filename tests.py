from uuid import uuid4

from getPlayers import *
import boto3

from datetime import datetime
session = boto3.Session(aws_access_key_id="AKIATCKANQTKSIM4LEMR", aws_secret_access_key="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")
dynamodb = session.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('pending-wagers')

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def do_test():
    c = 233
    for _ in range(0, 10):
        bet_id = str(uuid4())
        table.put_item(
                    Item={
                        'bet_id': str(bet_id),
                        'WhoMadeTheBet': "Higgins",
                        'TypeOfBet': "To get a Hit",
                        'PlayerBetOn': "Anthony Gose",
                        'Odds': c,
                        'Book': "DraftKings",
                        'TimeDatePlaced': now
                    }
        )
        c = c+13


do_test()