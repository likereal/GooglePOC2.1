from flask import Flask
import requests
import json
import pandas as pd
from io import StringIO

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
        print("Token Validation" + auth_json2['status'])
        if auth_json2['status'] == 'SUCCESS':
            expiresAt = auth_json2['tokenInfo']['expiresAt']
            print("Auth Token Validation" + auth_json2['status'])
            
            ExportProcess = "Export_from_anaplan"
        
            '''Getting Process from Anaplan'''
            auth_url = 'https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/processes'
            auth_json3= requests.get(
                url=auth_url,
                headers={
                    'Authorization': authToken
                }
            ).json()
            print("Getting Process from Anaplan " + auth_json3['status']['message'])
            if auth_json3['status']['message'] == 'Success':
                for process in auth_json3['processes']:
                    if ExportProcess == process['name']:
                        processID = process['id']
                        print("Anaplan Process ID " + processID)
                        '''Starting the Process'''
                        auth_url = f"https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/processes/{processID}/tasks"
                        auth_json4 = requests.post(
                            url=auth_url,
                            headers={
                                'Authorization': authToken,
                                'Content-type': 'application/json'
                            },
                            data = json.dumps({'localeName': 'en_US'})
                        ).json()
                        print("Anaplan Process Definition"+auth_json4['status']['message'])
                        if auth_json4['status']['message'] == 'Success':
                            taskID = auth_json4['task']['taskId']
                            print("Anaplan Process Task ID "+taskID)
                            '''Checking the Status of the Process'''
                            Flag = True
                            while Flag:
                                auth_url = f"https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/processes/{processID}/tasks/{taskID}"
                                auth_json5 = requests.get(
                                    url=auth_url,
                                    headers={
                                        'Authorization': authToken,
                                        'Content-type': 'application/json'
                                    }
                                ).json()
                                if auth_json5['task']['currentStep'] == "Failed.":
                                    print("Anaplan Process Failed")
                                elif auth_json5['task']['currentStep'] == "Complete.":
                                    print("Anaplan Process Complete")
                                    Flag = False
            '''Get files from anaplan'''
            url = f"https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/files/"
            getFileData = requests.get(
                url = url,
                headers = {
                    'Authorization': authToken
                }
            )
            getFileData_json = getFileData.json()
            print("Get Files from Anaplan"+ getFileData_json['status']['message'])

            if getFileData_json['status']['message'] == 'Success':
                file_info = getFileData_json['files'];
                
                for file in file_info:
                    if file['name'] == "Google_Demo.csv":
                        fileID = file['id']
                        url = f"https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/files/{fileID}/chunks/"
                        getChunk = requests.get(
                            url,
                            headers = {
                                'Authorization': authToken,
                                "Content-Type": "application/json"
                            }
                        )
                        getChunk = getChunk.json()
                        if getChunk['status']['message'] == "Success":
                            print(f"Getting the chunk count of {file['id']} COMPLETED")
                            for chunk in getChunk['chunks']:
                                url = f"https://api.anaplan.com/2/0/workspaces/8a868cdc7bd6c9ae017be5b938c83112/models/8B4052CB2DBE4E6AAEF8E96B968EFCCD/files/{fileID}/chunks/{chunk['id']}"
                                getChunk = requests.get(
                                    url,
                                    headers = {
                                        'Authorization': authToken,
                                        "Content-Type": "application/json"
                                    }
                                )
                                df = pd.read_csv(StringIO(getChunk.text), sep=",", index_col=['Time'])
                                return df.to_string(index = False)


if __name__ == '__main__':
    app.run()