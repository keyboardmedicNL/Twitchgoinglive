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
def discord_webhook_send(streamer_data: dict ) -> str: 
    username = streamer_data["data"][0]["user_name"]
    user = streamer_data["data"][0]["user_login"]
    title = streamer_data["data"][0]["title"]
    game = streamer_data["data"][0]["game_name"]
    viewers = streamer_data["data"][0]["viewer_count"]
    started = streamer_data["data"][0]["started_at"]
    thumbnail = streamer_data["data"][0]["thumbnail_url"]

    if streamer_data["data"][0]["game_name"] == "":
        game = "none"
    
    data_to_send_to_webhook = {"content": custom_message,"embeds": [
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
    
    send_request_to_discord = requests.post(webhook_url, json=data_to_send_to_webhook, params={'wait': 'true'})
    send_request_to_discord_json = send_request_to_discord.json()
    message_id = send_request_to_discord_json["id"]

    if send_request_to_discord.ok():
        if verbose >= 1:
            print(f"posting message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {send_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"posting message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {send_request_to_discord}",False)
    else:
        print(f"attempted to post message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {send_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to post message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {send_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to post message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {send_request_to_discord}","5")
        
    return(message_id)
    
# edits discord webhook message
def discord_webhook_edit(streamer_data: dict,message_id: str): 
    username = streamer_data["data"][0]["user_name"]
    user = streamer_data["data"][0]["user_login"]
    title = streamer_data["data"][0]["title"]
    game = streamer_data["data"][0]["game_name"]
    viewers = streamer_data["data"][0]["viewer_count"]
    started = streamer_data["data"][0]["started_at"]
    thumbnail = streamer_data["data"][0]["thumbnail_url"]

    if streamer_data["data"][0]["game_name"] == "":
        game = "none"
    
    data_to_send_to_webhook = {"content": custom_message, "embeds": [
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
    
    edit_request_to_discord = requests.patch(f"{webhook_url}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})
    
    if edit_request_to_discord.ok():
        if verbose >= 1:
            print(f"updating message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"updating message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}",False)
    else:
        print(f"attempted to update message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}","5")

# deletes discord webhook message
def discord_webhook_delete(message_id: str):
    delete_request_to_discord = requests.delete(f"{webhook_url}/messages/{message_id}", params={'wait': 'true'})
    if delete_request_to_discord.ok():
        if verbose >= 1:
            print(f"deleting message om discord with id: {message_id} for {streamer} with name {streamer_name}, response is {delete_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"deleting message om discord with id: {message_id} for {streamer} with name {streamer_name}, response is {delete_request_to_discord}",False)
    else:
        print(f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {delete_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {delete_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to delete message on discord with id: {message_id} for {streamer} with name {streamer_name}, response is {delete_request_to_discord}","5")

def webhook_offline(message_id: str ,filename: str):
    data_to_send_to_webhook = {"content": custom_message, "embeds": [
            {
            "title": f":x: {filename} has gone offline!",
            "description": "",
            "url": f"https://www.twitch.tv/{filename.lower()}",
            "color": 6570404,
            "fields": [
                {
                "name": "",
                "value": "[***get this bot***](https://github.com/keyboardmedicNL/Twitchgoinglive)"
                }
            ],
            }
        ]}
    
    edit_to_offline_request_to_discord = requests.patch(f"{webhook_url}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})

    if edit_to_offline_request_to_discord.ok():
        if verbose >= 1:
            print(f"updating to offline message to discord with id: {message_id} for {streamer} with name {username}, response is {edit_to_offline_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"updating to offline message to discord with discord id: {message_id} for {streamer} with name {username}, response is {edit_to_offline_request_to_discord}",False)
    else:
        print(f"attempted to update offline message to discord with id: {message_id} for {streamer} with name {username}, response is {edit_to_offline_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to update offlinee message to discord with discord id: {message_id} for {streamer} with name {username}, response is {edit_to_offline_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update offline message to discord with discord id: {message_id} for {streamer} with name {username}, response is {edit_to_offline_request_to_discord}","5")


# ===== twitch functions =====
# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        if verbose >= 1: 
            print("Requesting new api auth token from twitch")
            discord_remote_log("Goinglivebot","yellow","Requesting new api auth token from twitch",False)

        get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(twitch_api_id), "client_secret" : str(twitch_api_secret), "grant_type":"client_credentials"})
        
        if get_token_from_twitch_request.ok():
            get_token_from_twitch_json = get_token_from_twitch_request.json()
            token_from_twitch = get_token_from_twitch_json["access_token"]
            if verbose >= 1:
                print(f"new twitch api auth token is: {token_from_twitch}")
                discord_remote_log("Goinglivebot","green",f"new twitch api auth token recieved",False)
            with open(r'config/token.txt', 'w') as token_file:
                token_file.write("%s\n" % token_from_twitch)
        else:
            print(f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}")
            discord_remote_log("Goinglivebot","red",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}",True)
            send_gotify_notification("Clipbot",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}","5")
            token_from_twitch = "empty"
        return(token_from_twitch)

# gets stream information from twitch api
def get_stream_json_from_twitch(streamer: str) -> tuple[dict, dict, str, str, str]: 
    get_stream_json_from_twitch_request=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token}", 'Client-Id':twitch_api_id})
    print(f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}")

    if get_stream_json_from_twitch_request.ok():
        if verbose >= 1:
            discord_remote_log("Goinglivebot","green",f"got streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",False) 
    else:
            discord_remote_log("Goinglivebot","red",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",True)
            send_gotify_notification("Clipbot",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}","5")

    get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_request.json()

    try:
        is_live = get_stream_json_from_twitch_request_json["data"][0]["type"]
        stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
        streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]
        print(f"{streamer} with name {streamer_name} is live and in category {stream_category}!")
        discord_remote_log("Goinglivebot","green",f"{streamer} with name {streamer_name} is live and in category {stream_category}!",False)
    except:
        is_live = ""
        stream_category = ""
        streamer_name = ""

    return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)

# ===== other functions =====
# simple discord webhook send for remote logging
def discord_remote_log(title: str ,color: str ,description: str ,ping: str): 
    if use_discord_logs.lower() == "true":
        if color.lower() == "blue":
            color = 1523940
        elif color.lower() == "yellow":
            color = 14081792
        elif color.lower() == "red":
            color = 10159108
        elif color.lower() == "green":
            color = 703235
        elif color.lower() == "purple":
            color = 10622948
        elif color.lower() == "gray" or color.lower() == "grey":
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
        
        remote_log_send_request_to_discord = requests.post(discord_remote_log_url, json=data_for_log_hook, params={'wait': 'true'})
        if verbose >= 2:
            print(f"sending message to discord remote log webhook with title: {title} Color: {color} Description: {description} and ping: {ping_string} . Discord response is {str(remote_log_send_request_to_discord)}")
        
        time.sleep(1)

# gotify notification
def send_gotify_notification(title: str ,message: str ,priority: str):
    if use_gotify.lower() == "true":
        requests.post(gotifyurl, data={"title": title, "message": message, "priority":priority})

        if verbose >= 2:
            print(f"sending notification to gotify with title: {title} message: {message} priority: {priority}")

        time.sleep(1)

# saves streamid to file
def save_message_id_to_file(name: str ,message_id: str ,user_login: str):
    with open(f"config/embeds/{name}.txt", 'w') as file_to_save_message_id_to:
        file_to_save_message_id_to.write(message_id + '\n' + user_login)

    if verbose >= 1:
        print(f"message id: {message_id} and {user_login} saved in file {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {message_id} and {user_login} saved in file {name}.txt",False)

# reads streamid from file
def read_message_id_from_file(name: str) -> tuple[str, str]:
    with open(f"config/embeds/{name}.txt", 'r') as file_to_read_from:
        discord_webhook_message_id = str(file_to_read_from.readline())
        discord_webhook_message_id = message_id.strip("\n")
        name_in_file = str(file_to_read_from.readline())

    if verbose >= 1:
        print(f"message id : {discord_webhook_message_id} and {name_in_file} read from {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {discord_webhook_message_id} and {name_in_file} read from {name}.txt",False)

    return(discord_webhook_message_id,name_in_file)

# remove file
def remove_message_id_file(name: str):
    os.remove(f"config/embeds/{name}.txt")

    if verbose >= 1:
        print(f"removed file containing message id for embed for {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"removed file containing message id for embed for {name}.txt",False)

# gets list of streamers to poll
def get_streamers_from_file():
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
    token = get_token_from_twitch_api()

# ===== main code =====
# creates embeds folder if not exist allready
if not exists("config/embeds"):
    os.makedirs("config/embeds")
    print("embed folder was not found so it was created")
    discord_remote_log("Goinglivebot","blue","embed folder was not found so it was created",False)
# cleans up old messages on start
print("pulling list of streamers once to clean up old messages")
discord_remote_log("Goinglivebot","yellow","pulling list of streamers once to clean up old messages",False)
streamers,streamer_check = get_streamers_from_file()
for streamer in streamers:
    if exists(f"config/embeds/{streamer}.txt"):
        streamer_name = "unkown"
        message_id_from_file,name_from_file = read_message_id_from_file(streamer)
        if keep_messages:
            webhook_offline(message_id_from_file,name_from_file)
        else:
            discord_webhook_delete(message_id_from_file)
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
        streamers,streamer_check = get_streamers_from_file()
        if streamer_check:
            for streamer in streamers:
                rresponse,r,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                if not "200" in str(rresponse):
                    token = get_token_from_twitch_api()
                    rresponse,r,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                if is_live == "live" and (stream_category.lower() in categories or len(categories)==0):
                    if stream_category.lower() in categories:
                        print(f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories: {str(categories)}")
                        discord_remote_log("Goinglivebot","green",f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories",False)
                    if exists(f"config/embeds/{streamer}.txt"):
                        print(f"embed allready exsists for {streamer} with name {streamer_name}, updating it")
                        discord_remote_log("Goinglivebot","yellow",f"embed allready exsists for {streamer} with name {streamer_name}, updating it",False)
                        message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                        discord_webhook_edit(r,message_id_from_file)
                    else:
                        print(f"no embed exsists for {streamer} with name {streamer_name}, creating it")
                        discord_remote_log("Goinglivebot","yellow",f"no embed exsists for {streamer} with name {streamer_name}, creating it",False)
                        message_id = discord_webhook_send(r)
                        save_message_id_to_file(streamer,message_id,streamer_name)
                else:
                    if exists(f"config/embeds/{streamer}.txt"):
                        print(f"{streamer} with name {streamer_name} is no longer live")
                        discord_remote_log("Goinglivebot","yellow",f"{streamer} with name {streamer_name} is no longer live",False)
                        message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                        if keep_messages:
                            webhook_offline(message_id_from_file,name_from_file)
                        else:
                            discord_webhook_delete(message_id_from_file)
                        remove_message_id_file(streamer)
        else:
            print(f"there was an issue getting streamers from url")
            discord_remote_log("Goinglivebot","red",f"there was an issue getting streamers from url",True)
    except Exception as e:
        print(f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}")
        discord_remote_log("Goinglivebot","red",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}",True)
        send_gotify_notification("Clipbot",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}","5")
    print(f"finished main loop, waiting for {poll_interval} minutes")
    discord_remote_log("Goinglivebot","gray",f"finished main loop, waiting for {poll_interval} minutes",False)
    time.sleep(poll_interval*60)



