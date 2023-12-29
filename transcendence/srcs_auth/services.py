import requests
import os
import json

def get_access_token(code: str):
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
    if not response.ok:
        raise ValueError(f'Fail to get token, check data:\nData = {data}')
    credentials = response.json()
    return credentials.get('access_token')

def get_user_info(access_token: str):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('https://api.intra.42.fr/v2/me', headers=headers)
    if not response.ok:
        raise Exception(f'Fail to get user information, check token and headers:\nHeaders = {headers}\nToken = {access_token}')
    return response.json()

def exchange_code(code: str):
    access_token = get_access_token(code)
    user_info = get_user_info(access_token)
    return user_info
