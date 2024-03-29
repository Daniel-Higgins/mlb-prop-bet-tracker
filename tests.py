from getPlayers import *

mlb_players = fetch_mlb_players()
for player in mlb_players:
    print(player.get('FirstName', ''), player.get('LastName', ''), player.get('Team'))