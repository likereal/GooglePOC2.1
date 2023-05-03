from flask import Flask
import requests
import json

app = Flask(__name__)

@app.route('/')
def mainWork():
    username = "prabhu@relanto.ai"
    password = "Anaplan@April2023"
    
    auth_url = 'https://auth.anaplan.com/token/authenticate'
    auth_json = requests.post(
        url=auth_url,
        auth=(username, password)
    ).json()
    if auth_json['status'] == 'SUCCESS':
        authToken = 'AnaplanAuthToken ' + auth_json['tokenInfo']['tokenValue']
        print("AnaplanAuthToken" + auth_json['status'])
        
        '''Token Validation'''
        auth_url = 'https://auth.anaplan.com/token/validate'
        auth_json2 = requests.get(
            url=auth_url,
            headers={
                'Authorization': authToken
            }
        ).json()
        return "Token Validation" + auth_json2['status']


if __name__ == '__main__':
    app.run()