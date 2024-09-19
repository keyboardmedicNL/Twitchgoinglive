import time
import requests
import json
from os.path import exists
import os
import random
import shutil

# ===== webhook functions =====
# webhook send to discord for goinglive message
def webhook_send(rr):
    response = rr
    username = response["data"][0]["user_name"]
    user = response["data"][0]["user_login"]
    title = response["data"][0]["title"]
    game = response["data"][0]["game_name"]
    viewers = response["data"][0]["viewer_count"]
    started = response["data"][0]["started_at"]
    thumbnail = response["data"][0]["thumbnail_url"]

    if response["data"][0]["game_name"] == "":
        response["data"][0]["game_name"] = "none"
    data_for_hook = {"embeds": [
            {
            "title": f":red_circle: {username} is now live!",
            "description": title,
            "url": f"https://www.twitch.tv/{user}",
            "color": 6570404,
            "fields": [
                {
                    "name": "Playing:",
                    "value": game,
                    "inline": "true"
                },
                {
                    "name": "Viewers:",
                    "value": viewers,
                    "inline": "true"
                },
                {
                    "name": "Twitch:",
                    "value": f"[Watch stream](https://www.twitch.tv/{user})"
                }
            ],
            "timestamp": started,
            "image": {
                "url": f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{user}-640x360.jpg?cacheBypass={str(random.random())}"
            },
            "thumbnail": {
                "url": thumbnail
            },    
            }
        ]}
    rl = requests.post(webhook_url, json=data_for_hook, params={'wait': 'true'})
    rl_json = rl.json()
    message_id = rl_json["id"]
    if "200" in str(rl):
        print(f"posting message to discord with id: {message_id} for {streamer}, response is {rl}")
    else:
        print(f"attempted to post message to discord with id: {message_id} for {streamer}, response is {rl}")
    return(message_id)
    
# edits discord webhook message
def webhook_edit(rr,message_id): 
    response = rr
    username = response["data"][0]["user_name"]
    user = response["data"][0]["user_login"]
    title = response["data"][0]["title"]
    game = response["data"][0]["game_name"]
    viewers = response["data"][0]["viewer_count"]
    started = response["data"][0]["started_at"]
    thumbnail = response["data"][0]["thumbnail_url"]

    if response["data"][0]["game_name"] == "":
        response["data"][0]["game_name"] = "none"
    
    data_for_hook = {"embeds": [
            {
            "title": f":red_circle: {username} is now live!",
            "description": title,
            "url": f"https://www.twitch.tv/{user}",
            "color": 6570404,
            "fields": [
                {
                    "name": "Playing:",
                    "value": game,
                    "inline": "true"
                },
                {
                    "name": "Viewers:",
                    "value": viewers,
                    "inline": "true"
                },
                {
                    "name": "Twitch:",
                    "value": f"[Watch stream](https://www.twitch.tv/{user})"
                }
            ],
            "timestamp": started,
            "image": {
                "url": f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{user}-640x360.jpg?cacheBypass={str(random.random())}"
            },
            "thumbnail": {
                "url": thumbnail
            },    
            }
        ]}
    rl = requests.patch(f"{webhook_url}/messages/{message_id}", json=data_for_hook, params={'wait': 'true'})
    if "200" in str(rl):
        print(f"updating message to discord with id: {message_id} for {streamer}, response is {rl}")
    else:
        print(f"attempted to update message to discord with id: {message_id} for {streamer}, response is {rl}")

# deletes discord webhook message
def webhook_delete(message_id):
    rl = requests.delete(f"{webhook_url}/messages/{message_id}", params={'wait': 'true'})
    if "204" in str(rl):
        print(f"deleting message om discord with id: {message_id} for {streamer}, response is {rl}")
    else:
        print(f"attempted to delete message on discord with id: {message_id} for {streamer}, response is {rl}")

# ===== twitch functions =====
# renews token used for twitch api calls
def get_token(): 
        print("Requesting new twitch api auth token from twitch")
        response=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(twitch_api_id), "client_secret" : str(twitch_api_secret), "grant_type":"client_credentials"})
        if "200" in str(response):
            token_json = response.json()
            token = token_json["access_token"]
            print(f"new twitch api auth token is: {token}")
            with open(r'config/token.txt', 'w') as tokenFile:
                tokenFile.write("%s\n" % token)
        else:
            print(f"unable to request new twitch api auth token with response: {response}")
            token = "empty"
        return(token)

# gets stream information from twitch api
def get_stream(streamer): 
    response=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token}", 'Client-Id':twitch_api_id})
    print(f"tried to get streamer information with function get_stream for {streamer} with response: {response}")
    responsejson = response.json()
    try:
        is_live = responsejson["data"][0]["type"]
    except:
        is_live = ""
    return(response, responsejson, is_live)

# ===== other functions =====

# saves streamid to file
def save_message_id(name,message_id):
    fileName = f"config/embeds/{name}.txt"
    with open(fileName, 'w') as File:
        File.write(message_id)
    print(f"message id: {message_id} saved in file {name}.txt")

# reads streamid from file
def read_message_id(name):
    fileName = f"config/embeds/{name}.txt"
    with open(fileName, 'r') as File:
        message_id = str(File.readline())
    print(f"message id: {message_id} read from {name}.txt")
    return(message_id)

# remove file
def remove_message_id_file(name):
    os.remove(f"config/embeds/{name}.txt")
    print(f"removed file containing the message id for the embed for {name}.txt")

# gets list of streamers to poll
def get_streamers():
    with open("config/streamers.txt", 'r') as streamerfile:
        streamers = [line.rstrip() for line in streamerfile]
        if "http" in streamers[0]:
            response = requests.get(streamers[0])
            streamers = response.text.splitlines()
    print(f"list of streamers to poll from: {streamers}")
    return(streamers)

# ===== end of functions =====


# load config
with open("config/config.json") as config:
    config_json = json.load(config)
    twitch_api_id = str(config_json["twitch_api_id"])
    twitch_api_secret = str(config_json["twitch_api_secret"])
    webhook_url = str(config_json["discord_webhook_url"])
    poll_interval = int(config_json["poll_interval"])
print("succesfully loaded config")

#opens file to get auth token
if exists(f"config/token.txt"):
    with open("config/token.txt", 'r') as file2:
        tokenRaw = str(file2.readline())
        token = tokenRaw.strip()
    print ("twitch api auth token to use for auth: " + token)
else:
    token = get_token()

# ===== main code =====
# creates embeds folder
if not exists("config/embeds"):
    os.makedirs("config/embeds")
    print("embed folder was not found so it was created")
# cleans up old messages on start
print("pulling list of streamers once to remove old message")
streamers = get_streamers()
for streamer in streamers:
    if exists(f"config/embeds/{streamer}.txt"):
        message_id_from_file = read_message_id(streamer)
        webhook_delete(message_id_from_file)
        remove_message_id_file(streamer)
print("removed old messages posted to webhook")
for filename in os.listdir("config/embeds"):
    file_path = os.path.join("config/embeds", filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
print("removed all remaining files in config/embeds/")

# main loop
while True:
    try:
        streamers = get_streamers()
        for streamer in streamers:
            rresponse,r,is_live = get_stream(streamer)
            if not "200" in str(rresponse):
                token = get_token()
                rresponse,r,is_live = get_stream(streamer)
            if is_live == "live":
                if exists(f"config/embeds/{streamer}.txt"):
                    print(f"embed allready exsists for {streamer}, updating it")
                    message_id_from_file = read_message_id(streamer)
                    webhook_edit(r,message_id_from_file)
                else:
                    print(f"no embed exsists for {streamer}, creating it")
                    message_id = webhook_send(r)
                    save_message_id(streamer,message_id)
            else:
                if exists(f"config/embeds/{streamer}.txt"):
                    print(f"{streamer} is no longer live, deleting embed")
                    message_id_from_file = read_message_id(streamer)
                    webhook_delete(message_id_from_file)
                    remove_message_id_file(streamer)
    except Exception as e:
        print("An exception occurred in the main loop: ", str(e))
    print(f"main loop finished, waiting for {poll_interval} minutes")
    time.sleep(poll_interval*60)



