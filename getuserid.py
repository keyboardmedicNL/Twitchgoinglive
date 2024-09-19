import requests
import json
from getpass import getpass

#functions
def get_token(): 
        print("Requesting new twitch api auth token from twitch")
        response=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(twitch_api_id), "client_secret" : str(twitch_api_secret), "grant_type":"client_credentials"})
        if "200" in str(response):
            token_json = response.json()
            token = token_json["access_token"]
            print(f"new twitch api auth token succesfully requested")
        else:
            print(f"unable to request new twitch api auth token with response: {response}")
            token = "empty"
        return(token)

#main script
print ("Get twitch user id script:")
print("please input your twitch api id")
twitch_api_id= getpass("Twitch api id: ")
print("please input your twitch api secret")
twitch_api_secret = getpass("Twitch api secret: ")
token = get_token()
while True:
    user_name = input("please input the user name you would like to get the id for or press ctrl+c to stop this script at any time: ")
    response=requests.get(f"https://api.twitch.tv/helix/users?login={user_name.lower()}", headers={'Authorization':f"Bearer {token}", 'Client-Id':twitch_api_id})
    print(f"response for get users from twitch is {response}")
    responsejson = response.json()
    user_id = responsejson["data"][0]["id"]
    print(f"the user id for {user_name} = {user_id}")