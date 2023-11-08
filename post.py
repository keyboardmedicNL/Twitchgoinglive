# imports needed libraries
import requests
import time
import json
from datetime import datetime, timezone, timedelta

# formats embed for discord webhook and posts to url
def discord_remote_log(title,color,description): 
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
        data_for_log_hook = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(discord_remote_log_url, json=data_for_log_hook)
        time.sleep(1)

# loads needed data from config to variables
with open("config/config.json") as config: # opens config and stores data in variables
    config_json = json.load(config)
    remote_http_server_url = str(config_json["remote_http_server_url"])
    bot_name = str(config_json["bot_name"])
    post_interval = 60*int(config_json["post_interval"])
    use_discord_logs = str(config_json["use_discord_logs"])
    if use_discord_logs.lower() == "true":
        discord_remote_log_url = str(config_json["discord_remote_log_url"])
    print("<POST> Succesfully loaded config")
    discord_remote_log("Goinglivebot/post","blue","succesfully loaded config")

# main loop
while True:
    currentTime = (datetime.now(timezone.utc))
    currentTime = currentTime.timestamp()
    myobj = {'name': bot_name, 'time': currentTime} # formats currenttime in unix timestamp and bot_name into correct json formatting
    try:
        x = requests.post( remote_http_server_url, json = myobj) # sends post request
        print("<POST> webhook response is: " + x.text) # log message
        discord_remote_log("Goinglivebot/post","purple",f"webhook response is: {x.text}")
    except Exception as e: # catches exception
        print(f"An exception occurred in main loop: {str(e)}")
        discord_remote_log("Goinglivebot/post","red",f"An exception occurred in main loop: {str(e)}")
    time.sleep(post_interval)