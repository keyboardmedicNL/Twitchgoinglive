import time
import requests
from os.path import exists
import os
import random
import shutil
import yaml
from http.server import BaseHTTPRequestHandler, HTTPServer

# vars

default_config = {
    "twitch_api_id":"",
    "twitch_api_secret":"",
    "discord_webhook_url":"",
    "discord_remote_log_url":"",
    "web_server_url":"127.0.0.1",
    "poll_interval":10,
    "web_server_port":8888,
    "use_web_server":False,
    "use_discord_logs":False,
    "use_gotify":False,
    "gotify_url":"",
    "ping_id":"",
    "verbose":0,
    "allowed_categories":(),
    "message_before_embed":"",
    "use_offline_messages":False
}

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
    
    data_to_send_to_webhook = {"content": loaded_config["message_before_embed"],"embeds": [
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
    
    send_request_to_discord = requests.post(loaded_config["discord_webhook_url"], json=data_to_send_to_webhook, params={'wait': 'true'})
    send_request_to_discord_json = send_request_to_discord.json()
    message_id = send_request_to_discord_json["id"]

    if send_request_to_discord.ok:
        if loaded_config["verbose"] >= 1:
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
    
    data_to_send_to_webhook = {"content": loaded_config["message_before_embed"], "embeds": [
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
    
    edit_request_to_discord = requests.patch(f"{loaded_config["discord_webhook_url"]}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})
    
    if edit_request_to_discord.ok:
        if loaded_config["verbose"] >= 1:
            print(f"updating message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"updating message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}",False)
    else:
        print(f"attempted to update message to discord with id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update message to discord with discord id: {message_id} for {streamer} with name {streamer_name}, response is {edit_request_to_discord}","5")

# deletes discord webhook message
def discord_webhook_delete(message_id: str):
    delete_request_to_discord = requests.delete(f"{loaded_config["discord_webhook_url"]}/messages/{message_id}", params={'wait': 'true'})
    if delete_request_to_discord.ok:
        if loaded_config["verbose"] >= 1:
            print(f"deleting message om discord with id: {message_id}, response is {delete_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"deleting message om discord with id: {message_id}, response is {delete_request_to_discord}",False)
    else:
        print(f"attempted to delete message on discord with id: {message_id}, response is {delete_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to delete message on discord with id: {message_id}, response is {delete_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to delete message on discord with id: {message_id}, response is {delete_request_to_discord}","5")

# edits currently live embed to offline message
def discord_webhook_edit_to_offline(message_id: str ,filename: str):
    data_to_send_to_webhook = {"content": loaded_config["message_before_embed"], "embeds": [
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
    
    edit_to_offline_request_to_discord = requests.patch(f"{loaded_config["discord_webhook_url"]}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})

    if edit_to_offline_request_to_discord.ok:
        if loaded_config["verbose"] >= 1:
            print(f"updating to offline message to discord with id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}")
            discord_remote_log("Goinglivebot","green",f"updating to offline message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}",False)
    else:
        print(f"attempted to update offline message to discord with id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}")
        discord_remote_log("Goinglivebot","red",f"attempted to update offlinee message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update offline message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}","5")


# ===== twitch functions =====
# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        if loaded_config["verbose"] >= 1: 
            print("Requesting new api auth token from twitch")
            discord_remote_log("Goinglivebot","yellow","Requesting new api auth token from twitch",False)

        get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(loaded_config["twitch_api_id"]), "client_secret" : str(loaded_config["twitch_api_secret"]), "grant_type":"client_credentials"})
        
        if get_token_from_twitch_request.ok:
            get_token_from_twitch_json = get_token_from_twitch_request.json()
            token_from_twitch = get_token_from_twitch_json["access_token"]
            if loaded_config["verbose"] >= 1:
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
def get_stream_json_from_twitch(streamer: str) -> tuple[dict, dict, bool, str, str]: 
    get_stream_json_from_twitch_request=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token_from_twitch}", 'Client-Id':loaded_config["twitch_api_id"]})
    print(f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}")

    if get_stream_json_from_twitch_request.ok:
        if loaded_config["verbose"] >= 1:
            discord_remote_log("Goinglivebot","green",f"got streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",False) 
    else:
            discord_remote_log("Goinglivebot","red",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",True)
            send_gotify_notification("Clipbot",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}","5")

    get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_request.json()

    try:
        if str(get_stream_json_from_twitch_request_json["data"][0]["type"]).lower() == "live":
            is_live = True
        else:
            is_live = False
        stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
        streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]
        print(f"{streamer} with name {streamer_name} is live and in category {stream_category}!")
        discord_remote_log("Goinglivebot","green",f"{streamer} with name {streamer_name} is live and in category {stream_category}!",False)
    except:
        is_live = False
        stream_category = ""
        streamer_name = ""

    return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)

# ===== other functions =====
# simple discord webhook send for remote logging
def discord_remote_log(title: str ,color: str ,description: str ,ping: bool): 
    if loaded_config["use_discord_logs"]:
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
            ping_string = f"<@{loaded_config["ping_id"]}>"
        else:
            ping_string = ""
        
        data_for_log_hook = {"content": ping_string, "embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        
        remote_log_send_request_to_discord = requests.post(loaded_config["discord_remote_log_url"], json=data_for_log_hook, params={'wait': 'true'})
        if loaded_config["verbose"] >= 2:
            print(f"sending message to discord remote log webhook with title: {title} Color: {color} Description: {description} and ping: {ping_string} . Discord response is {str(remote_log_send_request_to_discord)}")
        
        time.sleep(1)

# gotify notification
def send_gotify_notification(title: str ,message: str ,priority: str):
    if loaded_config["use_gotify"]:
        requests.post(loaded_config["gotify_url"], data={"title": title, "message": message, "priority":priority})

        if loaded_config["verbose"] >= 2:
            print(f"sending notification to gotify with title: {title} message: {message} priority: {priority}")

        time.sleep(1)

# saves streamid to file
def save_message_id_to_file(name: str ,message_id: str ,user_login: str):
    with open(f"config/embeds/{name}.txt", 'w') as file_to_save_message_id_to:
        file_to_save_message_id_to.write(message_id + '\n' + user_login)

    if loaded_config["verbose"] >= 1:
        print(f"message id: {message_id} and {user_login} saved in file {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {message_id} and {user_login} saved in file {name}.txt",False)

# reads streamid from file
def read_message_id_from_file(name: str) -> tuple[str, str]:
    with open(f"config/embeds/{name}.txt", 'r') as file_to_read_from:
        discord_webhook_message_id = str(file_to_read_from.readline())
        discord_webhook_message_id = discord_webhook_message_id.strip("\n")
        name_in_file = str(file_to_read_from.readline())

    if loaded_config["verbose"] >= 1:
        print(f"message id : {discord_webhook_message_id} and {name_in_file} read from {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"message id: {discord_webhook_message_id} and {name_in_file} read from {name}.txt",False)

    return(discord_webhook_message_id,name_in_file)

# remove file
def remove_message_id_file(name: str):
    os.remove(f"config/embeds/{name}.txt")

    if loaded_config["verbose"] >= 1:
        print(f"removed file containing message id for embed for {name}.txt")
        discord_remote_log("Goinglivebot","blue",f"removed file containing message id for embed for {name}.txt",False)

# gets list of streamers to poll
def get_streamers_from_file() -> tuple[list, bool]:
    with open("config/streamers.txt", 'r') as file_with_streamer_ids:
        list_of_streamers = [line.rstrip() for line in file_with_streamer_ids]
        if "http" in list_of_streamers[0]:
            get_streamers_trough_request_response = requests.get(list_of_streamers[0])

            if not get_streamers_trough_request_response.ok:
                print(f"was unable to get list of streamers trough request with response: {get_streamers_trough_request_response}")
                discord_remote_log("Goinglivebot","red",f"was unable to get list of streamers trough request with response: {get_streamers_trough_request_response}",False)
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
            else:
                list_of_streamers = get_streamers_trough_request_response.text.splitlines()
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
        else:
            is_get_streamers_from_file_succesfull = True

    print(f"list of streamers to poll from: {list_of_streamers}")
    discord_remote_log("Goinglivebot","yellow",f"list of streamers to poll from: {list_of_streamers}",False)

    return(list_of_streamers, is_get_streamers_from_file_succesfull)

# loads config from file
def load_config(default_config: dict) -> dict:
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)
        merged_config = {**default_config, **config_yaml}

    print("succesfully loaded config")

    return(merged_config)

#opens file to get auth token
def read_twitch_api_token_from_file() -> str:
    if exists(f"config/token.txt"):
        with open("config/token.txt", 'r') as file_with_twitch_token:
            token_raw = str(file_with_twitch_token.readline())
            twitch_api_token = token_raw.strip()
        print ("Token to use for twitch api auth: " + twitch_api_token)
        discord_remote_log("Goinglivebot","blue","twitch api auth token loaded succesfully",False)
    else:
        twitch_api_token = get_token_from_twitch_api()
        
    return(twitch_api_token)

# creates embeds folder if not exist allready
def create_embeds_folder():
    if not exists("config/embeds"):
        os.makedirs("config/embeds")
        print("embed folder was not found so it was created")
        discord_remote_log("Goinglivebot","blue","embed folder was not found so it was created",False)

# clean op old embeds
def clean_up_old_embeds(list_of_streamers: list ,use_offline_message: bool):
    print("pulling list of streamers once to clean up old messages")
    discord_remote_log("Goinglivebot","yellow","pulling list of streamers once to clean up old messages",False)
    for streamer in list_of_streamers:
        if exists(f"config/embeds/{streamer}.txt"):
            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
            if use_offline_message:
                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
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

# ===== end of functions =====


# ===== main code =====
loaded_config = load_config(default_config)
create_embeds_folder()
# gets list of streamers once to clean up old embeds, ends script if it fails to get list of streamers
token_from_twitch = read_twitch_api_token_from_file()
streamers, streamer_get_was_succesfull = get_streamers_from_file()

if streamer_get_was_succesfull:
    clean_up_old_embeds(streamers, loaded_config["use_offline_messages"])

    # main loop
    while True:
        try:
            streamers, streamer_get_was_succesfull = get_streamers_from_file()
            if streamer_get_was_succesfull:
                for streamer in streamers:
                    # sets streamer name incase an exception is called before streamer_name is set with a function
                    streamer_name = "unknown"

                    get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                    if not get_stream_json_from_twitch_response.ok:
                        token_from_twitch = get_token_from_twitch_api()
                        get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                    
                    if is_live and (stream_category.lower() in loaded_config["allowed_categories"] or len(loaded_config["allowed_categories"])==0):
                        
                        if stream_category.lower() in loaded_config["allowed_categories"]:
                            print(f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories: {str(loaded_config["allowed_categories"])}")
                            discord_remote_log("Goinglivebot","green",f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories",False)
                        
                        if exists(f"config/embeds/{streamer}.txt"):
                            print(f"embed allready exsists for {streamer} with name {streamer_name}, updating it")
                            discord_remote_log("Goinglivebot","yellow",f"embed allready exsists for {streamer} with name {streamer_name}, updating it",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            discord_webhook_edit(get_stream_json_from_twitch_data,message_id_from_file)
                        else:
                            print(f"no embed exsists for {streamer} with name {streamer_name}, creating it")
                            discord_remote_log("Goinglivebot","yellow",f"no embed exsists for {streamer} with name {streamer_name}, creating it",False)
                            message_id = discord_webhook_send(get_stream_json_from_twitch_data)
                            save_message_id_to_file(streamer,message_id,streamer_name)
                    
                    else:
                        
                        if exists(f"config/embeds/{streamer}.txt"):
                            print(f"{streamer} with name {streamer_name} is no longer live")
                            discord_remote_log("Goinglivebot","yellow",f"{streamer} with name {streamer_name} is no longer live",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            
                            if loaded_config["use_offline_messages"]:
                                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
                            else:
                                discord_webhook_delete(message_id_from_file)
                            remove_message_id_file(streamer)
        
        except Exception as e:
            print(f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}")
            discord_remote_log("Goinglivebot","red",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}",True)
            send_gotify_notification("Clipbot",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}","5")
        
        # start webserver
        if loaded_config["use_web_server"]:
            try:
                print("starting webserver for 10 seconds")
                class MyServer(BaseHTTPRequestHandler):
                    def do_GET(self):
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
                        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
                        self.wfile.write(bytes("<body>", "utf-8"))
                        self.wfile.write(bytes("<p>Hello, i am a webserver.</p>", "utf-8"))
                        self.wfile.write(bytes("</body></html>", "utf-8"))

                if __name__ == "__main__":        
                    webServer = HTTPServer((loaded_config["web_server_url"], loaded_config["web_server_port"]), MyServer)
                    print("Server started http://%s:%s" % (loaded_config["web_server_url"], loaded_config["web_server_port"]))
                    #discord_remote_log("Goinglivebot/webserver","purple","Server started http://%s:%s" % (loaded_config["web_server_url"], loaded_config["web_server_port"]))
                    webServer.serve_forever()
                    print(f"finished main loop and running webserver, waiting for {loaded_config["poll_interval"]} minutes")
                    discord_remote_log("Goinglivebot","gray",f"finished main loop and running webserver, waiting for {loaded_config["poll_interval"]} minutes",False)
                    time.sleep(loaded_config["poll_interval"]*60)
                    webServer.shutdown()
            except Exception as e:
                    print(f"An exception occurred in main loop: {str(e)}")
                    #discord_remote_log("Goinglivebot/webserver","red",f"An exception occurred in main loop: {str(e)}")

        else:
            print(f"finished main loop, waiting for {loaded_config["poll_interval"]} minutes")
            discord_remote_log("Goinglivebot","gray",f"finished main loop, waiting for {loaded_config["poll_interval"]} minutes",False)
            time.sleep(loaded_config["poll_interval"]*60)
else:
    print(f"unable to get streamers from file, stopping script....")



