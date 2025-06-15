import time
import requests
import json
import threading
from subprocess import call
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
    data_for_hook = {"content": custom_message,"embeds": [
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
                },
                {
                "name": "",
                "value": "[***get this bot***](https://github.com/keyboardmedicNL/Twitchgoinglive)"
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
        if verbose >= 1:
            print(f"posting message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
            discord_remote_log("Goinglivebot","green",f"posting message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",False)
    else:
        print(f"attempted to post message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
        discord_remote_log("Goinglivebot","red",f"attempted to post message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",True)
        gotify("Clipbot",f"attempted to post message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}","5")
        
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
    
    data_for_hook = {"content": custom_message, "embeds": [
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
                },
                {
                "name": "",
                "value": "[***get this bot***](https://github.com/keyboardmedicNL/Twitchgoinglive)"
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
        if verbose >= 1:
            print(f"updating message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
            discord_remote_log("Goinglivebot","green",f"updating message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",False)
    else:
        print(f"attempted to update message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
        discord_remote_log("Goinglivebot","red",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",True)
        gotify("Clipbot",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {rl}","5")

# deletes discord webhook message
def webhook_delete(message_id):
    rl = requests.delete(f"{webhook_url}/messages/{message_id}", params={'wait': 'true'})
    if "204" in str(rl):
        if verbose >= 1:
            print(f"deleting message om discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
            discord_remote_log("Goinglivebot","green",f"deleting message om discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",False)
    else:
        print(f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}")
        discord_remote_log("Goinglivebot","red",f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}",True)
        gotify("Clipbot",f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {rl}","5")

def webhook_offline(message_id,filename):
    username = filename
    
    data_for_hook = {"content": custom_message, "embeds": [
            {
            "title": f":x: {username} has gone offline!",
            "description": "",
            "url": f"https://www.twitch.tv/{username.lower()}",
            "color": 6570404,
            "fields": [
                {
                "name": "",
                "value": "[***get this bot***](https://github.com/keyboardmedicNL/Twitchgoinglive)"
                }
            ],
            }
        ]}
    rl = requests.patch(f"{webhook_url}/messages/{message_id}", json=data_for_hook, params={'wait': 'true'})
    if "200" in str(rl):
        if verbose >= 1:
            print(f"updating to offline message to discord with id: {message_id} for {streamer} with name {username}, response is {rl}")
            discord_remote_log("Goinglivebot","green",f"updating to offline message to discord with discord id: {message_id} for {streamer} with name {username}, response is {rl}",False)
    else:
        print(f"attempted to update offline message to discord with id: {message_id} for {streamer} with name {username}, response is {rl}")
        discord_remote_log("Goinglivebot","red",f"attempted to update offlinee message to discord with discord id: {message_id} for {streamer} with name {username}, response is {rl}",True)
        gotify("Clipbot",f"attempted to update offline message to discord with discord id: {message_id} for {streamer} with name {username}, response is {rl}","5")


# ===== twitch functions =====
# renews token used for twitch api calls
def get_token():
        if verbose >= 1: 
            print("Requesting new api auth token from twitch")
            discord_remote_log("Goinglivebot","yellow","Requesting new api auth token from twitch",False)
        response=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(twitch_api_id), "client_secret" : str(twitch_api_secret), "grant_type":"client_credentials"})
        if "200" in str(response):
            token_json = response.json()
            token = token_json["access_token"]
            if verbose >= 1:
                print(f"new twitch api auth token is: {token}")
                discord_remote_log("Goinglivebot","green",f"new twitch api auth token recieved",False)
            with open(r'config/token.txt', 'w') as tokenFile:
                tokenFile.write("%s\n" % token)
        else:
            print(f"unable to request new twitch api auth token with response: {response}")
            discord_remote_log("Goinglivebot","red",f"unable to request new twitch api auth token with response: {response}",True)
            gotify("Clipbot",f"unable to request new twitch api auth token with response: {response}","5")
            token = "empty"
        return(token)

# gets stream information from twitch api
def get_stream(streamer): 
    response=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token}", 'Client-Id':twitch_api_id})
    print(f"tried to get streamer information with function get_stream for {streamer} with response: {response}")
    if "200" in str(response):
        if verbose >= 1:
            discord_remote_log("Goinglivebot","green",f"got streamer information with function get_stream for {streamer} with response: {response}",False) 
    else:
            discord_remote_log("Goinglivebot","red",f"tried to get streamer information with function get_stream for {streamer} with response: {response}",True)
            gotify("Clipbot",f"tried to get streamer information with function get_stream for {streamer} with response: {response}","5")
    responsejson = response.json()
    try:
        is_live = responsejson["data"][0]["type"]
        stream_category = responsejson["data"][0]["game_name"]
        streamer_name = responsejson["data"][0]["user_name"]
        print(f"{streamer} with name {streamer_name} is live and in category {stream_category}!")
        discord_remote_log("Goinglivebot","green",f"{streamer} with name {streamer_name} is live and in category {stream_category}!",False)
    except:
        is_live = ""
        stream_category = ""
        streamer_name = ""
    return(response, responsejson, is_live, stream_category, streamer_name)

# ===== other functions =====
# simple discord webhook send for remote logging
def discord_remote_log(title,color,description,ping): 
    if use_discord_logs.lower() == "true":
        if color == "blue":
            color = 1523940
        elif color == "yellow":
            color = 14081792
        elif color == "red":
            color = 10159108
        elif color == "green":
            color = 703235
        elif color == "purple":
            color = 10622948
        elif color == "gray" or color == "grey":
            color = 1776669
        if ping:
            ping_string = f"<@{ping_id}>"
        else:
            ping_string = ""
        data_for_log_hook = {"content": ping_string, "embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(discord_remote_log_url, json=data_for_log_hook, params={'wait': 'true'})
        if verbose >= 2:
            print(f"sending message to discord remote log webhook with title: {title} Color: {color} Description: {description} and ping: {ping_string} . Discord response is {str(rl)}")
        time.sleep(1)

# gotify notification
def gotify(title,message,priority):
    if use_gotify.lower() == "true":
        gr = requests.post(gotifyurl, data={"title": title, "message": message, "priority":priority})
        if verbose >= 2:
            print(f"sending notification to gotify with title: {title} message: {message} priority: {priority}")
        time.sleep(1)

# saves streamid to file
def save_message_id(name,message_id,user_login):
    fileName = f"config/embeds/{name}.txt"
    with open(fileName, 'w') as File:
        File.write(message_id + '\n' + user_login)
    if verbose >= 1:
        print(f"message id: {message_id} and {user_login} saved in file {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {message_id} and {user_login} saved in file {name}.txt",False)

# reads streamid from file
def read_message_id(name):
    fileName = f"config/embeds/{name}.txt"
    with open(fileName, 'r') as File:
        message_id = str(File.readline())
        message_id = message_id.strip("\n")
        name_in_file = str(File.readline())
    if verbose >= 1:
        print(f"message id : {message_id} and {name_in_file} read from {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {message_id} and {name_in_file} read from {name}.txt",False)
    return(message_id,name_in_file)

# remove file
def remove_message_id_file(name):
    os.remove(f"config/embeds/{name}.txt")
    if verbose >= 1:
        print(f"removed file containing message id for embed for {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"removed file containing message id for embed for {name}.txt",False)

# gets list of streamers to poll
def get_streamers():
    streamer_check = True
    with open("config/streamers.txt", 'r') as streamerfile:
        streamers = [line.rstrip() for line in streamerfile]
        if "http" in streamers[0]:
            response = requests.get(streamers[0])
            streamers = response.text.splitlines()
            if "200" not in str(response):
                streamer_check = False
    print(f"list of streamers to poll from: {streamers}")
    discord_remote_log("Goinglivebot","yellow",f"list of streamers to poll from: {streamers}",False)
    return(streamers, streamer_check)

# ===== end of functions =====


# load config
with open("config/config.json") as config:
    config_json = json.load(config)
    twitch_api_id = str(config_json["twitch_api_id"])
    twitch_api_secret = str(config_json["twitch_api_secret"])
    webhook_url = str(config_json["discord_webhook_url"])
    poll_interval = int(config_json["poll_interval"])
    use_web_server = str(config_json["use_web_server"])
    use_remote_post = str(config_json["use_remote_post"])
    use_gotify = str(config_json["use_gotify"])
    if use_gotify.lower() == "true":
        gotifyurl = str(config_json["gotifyurl"])
    ping_id = str(config_json["pingid"])
    verbose = int(config_json["verbose"])
    gotifyurl = str(config_json["gotifyurl"])
    use_discord_logs = str(config_json["use_discord_logs"])
    if use_discord_logs.lower() == "true":
        discord_remote_log_url = str(config_json["discord_remote_log_url"])
    categories = config_json["categories"]
    custom_message = str(config_json["message"])
    keep_messages = str(config_json["keep_messages_when_offline"])
    if keep_messages.lower() == "true":
        keep_messages = True
    else:
        keep_messages = False
discord_remote_log("Goinglivebot","blue","succesfully loaded config",False)
print("succesfully loaded config")

# webserver for local monitoring
if use_web_server.lower() == "true":
    def thread_second(): # start webserver.py as a second threat to allow it to run parallel with main script
        call(["python", "webserver.py"])
    process_thread = threading.Thread(target=thread_second)
    process_thread.start()
    print("starting webserver for local monitoring") 
    discord_remote_log("Goinglivebot","blue","starting webserver for local monitoring",False)

#post process to talk to remote monitor
if use_remote_post.lower() == "true":
    def thread_third(): # start post.py as a third threat to allow it to run parallel with main script
        call(["python", "post.py"])
    process_thread = threading.Thread(target=thread_third)
    process_thread.start()
    print("starting post server for remote monitoring")
    discord_remote_log("Goinglivebot","blue","starting post server for remote monitoring",False)

#opens file to get auth token
if exists(f"config/token.txt"):
    with open("config/token.txt", 'r') as file2:
        tokenRaw = str(file2.readline())
        token = tokenRaw.strip()
    print ("Token to use for twitch api auth: " + token)
    discord_remote_log("Goinglivebot","blue","twitch api auth token loaded succesfully",False)
else:
    token = get_token()

# ===== main code =====
# creates embeds folder if not exist allready
if not exists("config/embeds"):
    os.makedirs("config/embeds")
    print("embed folder was not found so it was created")
    discord_remote_log("Goinglivebot","blue","embed folder was not found so it was created",False)
# cleans up old messages on start
print("pulling list of streamers once to clean up old messages")
discord_remote_log("Goinglivebot","yellow","pulling list of streamers once to clean up old messages",False)
streamers,streamer_check = get_streamers()
for streamer in streamers:
    if exists(f"config/embeds/{streamer}.txt"):
        streamer_name = "unkown"
        message_id_from_file,name_from_file = read_message_id(streamer)
        if keep_messages:
            webhook_offline(message_id_from_file,name_from_file)
        else:
            webhook_delete(message_id_from_file)
        remove_message_id_file(streamer)
print("cleaned up old embeds posted to webhook")
for filename in os.listdir("config/embeds"):
    file_path = os.path.join("config/embeds", filename)
    if os.path.isfile(file_path) or os.path.islink(file_path):
        os.unlink(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)
print("removed all remaining files in config/embeds/")
discord_remote_log("Goinglivebot","blue","cleaned up old embeds posted to webhook and cleaned embeds folder",False)

# main loop
while True:
    try:
        streamers,streamer_check = get_streamers()
        if streamer_check:
            for streamer in streamers:
                rresponse,r,is_live,stream_category,streamer_name = get_stream(streamer)
                if not "200" in str(rresponse):
                    token = get_token()
                    rresponse,r,is_live,stream_category,streamer_name = get_stream(streamer)
                if is_live == "live" and (stream_category.lower() in categories or len(categories)==0):
                    if stream_category.lower() in categories:
                        print(f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories: {str(categories)}")
                        discord_remote_log("Goinglivebot","green",f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories",False)
                    if exists(f"config/embeds/{streamer}.txt"):
                        print(f"embed allready exsists for {streamer} with name {streamer_name}, updating it")
                        discord_remote_log("Goinglivebot","yellow",f"embed allready exsists for {streamer} with name {streamer_name}, updating it",False)
                        message_id_from_file,name_from_file = read_message_id(streamer)
                        webhook_edit(r,message_id_from_file)
                    else:
                        print(f"no embed exsists for {streamer} with name {streamer_name}, creating it")
                        discord_remote_log("Goinglivebot","yellow",f"no embed exsists for {streamer} with name {streamer_name}, creating it",False)
                        message_id = webhook_send(r)
                        save_message_id(streamer,message_id,streamer_name)
                else:
                    if exists(f"config/embeds/{streamer}.txt"):
                        print(f"{streamer} with name {streamer_name} is no longer live")
                        discord_remote_log("Goinglivebot","yellow",f"{streamer} with name {streamer_name} is no longer live",False)
                        message_id_from_file,name_from_file = read_message_id(streamer)
                        if keep_messages:
                            webhook_offline(message_id_from_file,name_from_file)
                        else:
                            webhook_delete(message_id_from_file)
                        remove_message_id_file(streamer)
        else:
            print(f"there was an issue getting streamers from url")
            discord_remote_log("Goinglivebot","red",f"there was an issue getting streamers from url",True)
    except Exception as e:
        print(f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}")
        discord_remote_log("Goinglivebot","red",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}",True)
        gotify("Clipbot",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}","5")
    print(f"finished main loop, waiting for {poll_interval} minutes")
    discord_remote_log("Goinglivebot","gray",f"finished main loop, waiting for {poll_interval} minutes",False)
    time.sleep(poll_interval*60)



