import requests
import os

def exchange_code(code: str):
    data = {
        "client_id": os.environ.get('CLIENT_ID'),
        "client_secret": os.environ.get('CLIENT_SECRET'),
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ.get('REDIRECT_URI'),
        "scope": "identify"
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post("https://api.intra.42.fr/oauth/token", data=data, headers=headers)
    credentials = response.json()
    access_token = credentials['access_token']
    response = requests.get('https://api.intra.42.fr/v2/me', headers={'Authorization': 'Bearer %s' % access_token})
    user = response.json()
    return user