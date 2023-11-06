import time
import requests
import json
import threading
from subprocess import call
from os.path import exists
import os
import random

# ===== webhook functions =====
# webhook send to discord for goinglive message
def webhooksend(rr):
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
    data = {"embeds": [
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
    rl = requests.post(webhookurl, json=data, params={'wait': 'true'})
    rljson = rl.json()
    messageid = rljson["id"]
    print(f"discord webhook response for method post is {rl} ({messageid} posted)")
    discordremotelog("Goinglivebot",14081792,f"discord webhook response for method post is {rl} ({messageid} posted)")
    return(messageid)
    
# edits discord webhook message
def webhookedit(rr,messageid): 
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
    
    data = {"embeds": [
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
                "url": f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{user}-640x360.jpg?cacheBypass=300"
            },
            "thumbnail": {
                "url": thumbnail
            },    
            }
        ]}
    rl = requests.patch(f"{webhookurl}/messages/{messageid}", json=data, params={'wait': 'true'})
    print(f"discord webhook response for method patch is {rl} ({messageid} updated)")
    discordremotelog("Goinglivebot",14081792,f"discord webhook response for method patch is {rl} ({messageid} updated)")

# deletes discord webhook message
def webhookdelete(messageid):
    rl = requests.delete(f"{webhookurl}/messages/{messageid}", params={'wait': 'true'})
    print(f"discord webhook response for method delete is {rl} ({messageid} removed)")
    discordremotelog("Goinglivebot",14081792,f"discord webhook response for method delete is {rl} ({messageid} removed)")

# ===== twitch functions =====
# renews token used for twitch api calls
def gettoken(): 
        print("Requesting new token from twitch")
        response=requests.post("https://id.twitch.tv/oauth2/token", data={"client_id" : str(twitchClientId), "client_secret" : str(twitchSecret), "grant_type":"client_credentials"})
        tokenJson = response.json()
        token = tokenJson["access_token"]
        print(f"new token is: {token}")
        discordremotelog("Goinglivebot",14081792,f"new auth token requested")
        with open(r'config/token.txt', 'w') as tokenFile:
            tokenFile.write("%s\n" % token)
        return(token)

# gets stream information from twitch api
def getstream(streamer): 
    response=requests.get(f"https://api.twitch.tv/helix/streams?&user_login={streamer}", headers={'Authorization':f"Bearer {token}", 'Client-Id':twitchClientId})
    print(f"response for getstream with name {streamer} is {response}")
    discordremotelog("Goinglivebot",14081792,f"response for getstream with name {streamer} is {response}")
    responsejson = response.json()
    try:
        islive = responsejson["data"][0]["type"]
    except:
        islive = ""
    return(response, responsejson, islive)

# ===== other functions =====
# simple discord webhook send for remote logging
def discordremotelog(title,color,description): 
    if webhooklogurl != "":
        data = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(webhooklogurl, json=data)
        time.sleep(1)

# saves streamid to file
def savemessageid(name,messageid):
    fileName = f"config/{name}.txt"
    with open(fileName, 'w') as File:
        File.write(messageid)
    print(f"{messageid} saved in file {name}.txt")
    discordremotelog("Goinglivebot",14081792,f"{messageid} saved in file {name}.txt")

# reads streamid from file
def readmessageid(name):
    fileName = f"config/{name}.txt"
    with open(fileName, 'r') as File:
        messageid = str(File.readline())
    print(f"{messageid} read from {name}.txt")
    discordremotelog("Goinglivebot",14081792,f"{messageid} read from {name}.txt")
    return(messageid)

# remove file
def removemessageidfile(name):
    os.remove(f"config/{name}.txt")
    print(f"removed file {name}.txt")
    discordremotelog("Goinglivebot",14081792,f"removed file {name}.txt")

# gets list of streamers to poll
def getstreamers():
    with open("config/streamers.txt", 'r') as streamerfile:
        streamers = [line.rstrip() for line in streamerfile]
        if "http" in streamers[0]:
            response = requests.get(streamers[0])
            streamers = response.text.splitlines()
    return(streamers)

# ===== end of functions =====


# load config
with open("config/config.json") as config:
    configJson = json.load(config)
    twitchClientId = configJson["twitchClientId"]
    twitchSecret = configJson["twitchSecret"]
    webhookurl = configJson["webhookurl"]
    webhooklogurl = configJson["webhooklogurl"]
    webhookmonitorurl = configJson["webhookmonitorurl"]
    checktime = configJson["checktime"]
    config.close()
discordremotelog("Goinglivebot",14081792,"succesfully loaded config")
print("succesfully loaded config")

# webserver for local monitoring
def thread_second(): # start webserver.py as a second threat to allow it to run parallel with main script
    call(["python", "webserver.py"])
processThread = threading.Thread(target=thread_second)
processThread.start()
print("starting webserver for local monitoring") 
discordremotelog("Goinglivebot",14081792,"starting webserver for local monitoring")

#post process to talk to remote monitor
if webhookmonitorurl != "":
    def thread_third(): # start post.py as a third threat to allow it to run parallel with main script
        call(["python", "post.py"])
    processThread = threading.Thread(target=thread_third)
    processThread.start()
    print("starting post server for remote monitoring")
    discordremotelog("Goinglivebot",14081792,"starting post server for remote monitoring")

#opens file to get auth token
if exists(f"config/token.txt"):
    with open("config/token.txt", 'r') as file2:
        tokenRaw = str(file2.readline())
        token = tokenRaw.strip()
    print ("Token to use for auth: " + token)
    discordremotelog("Goinglivebot",14081792,"auth token loaded succesfully")
else:
    token = gettoken()

# ===== main code =====
# cleans up old messages on start
streamers = getstreamers()
for streamer in streamers:
    if exists(f"config/{streamer}.txt"):
        messageidfromfile = readmessageid(streamer)
        webhookdelete(messageidfromfile)
        removemessageidfile(streamer)
print("removed old messages posted to webhook")
discordremotelog("Goinglivebot",14081792,"removed old messages posted to webhook")

# main loop
while True:
    try:
        streamers = getstreamers()
        for streamer in streamers:
            rresponse,r,islive = getstream(streamer)
            if "401" in str(rresponse):
                token = gettoken()
                rresponse,r,islive = getstream(streamer)
            if islive == "live":
                if exists(f"config/{streamer}.txt"):
                    messageidfromfile = readmessageid(streamer)
                    webhookedit(r,messageidfromfile)
                else:
                    messageid = webhooksend(r)
                    savemessageid(streamer,messageid)
            else:
                if exists(f"config/{streamer}.txt"):
                    messageidfromfile = readmessageid(streamer)
                    webhookdelete(messageidfromfile)
                    removemessageidfile(streamer)
        print(f"waiting for {checktime} minutes")
        discordremotelog("Goinglivebot",14081792,f"waiting for {checktime} minutes")
    except Exception as e:
        print("An exception occurred: ", str(e))
    print()
    time.sleep(checktime*60)



