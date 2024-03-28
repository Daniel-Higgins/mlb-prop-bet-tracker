import requests

api_key = 'ae9d60ebe445446e8b4cc35c45dfdfea'
url = f'https://api.sportsdata.io/v3/mlb/scores/json/Players?key={api_key}'  # Modify based on correct endpoint

headers = {
    'Ocp-Apim-Subscription-Key': api_key,
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    players = response.json()
    # Now you can process the 'players' data
else:
    print("Failed to retrieve data:", response.status_code)
