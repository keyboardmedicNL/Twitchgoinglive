# imports needed libraries
import requests
import time
import json
from datetime import datetime, timezone, timedelta

# variables used in script
configcheck = False

# formats embed for discord webhook and posts to url
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

# loads needed data from config to variables
while configcheck == False: # loop to ensure config gets loaded
    try:
        with open("config/config.json") as config: # opens config and stores data in variables
            configJson = json.load(config)
            webhookmonitorurl = configJson["webhookmonitorurl"]
            botname = configJson["botname"]
            timeout = 60*int(configJson["posttimeout"])
            webhooklogurl = configJson["webhooklogurl"]
            config.close()
            configcheck = True # stops loop if succesfull
            print("<POST> Succesfully loaded config")
            discordremotelog("Goinglivebot/post",14081792,"succesfully loaded config")
    except Exception as e: # catches exception
        print(f"An exception occurred whilst trying to read the config: {str(e)} waiting for 1 minute")
        time.sleep(60)

# main loop
while True:
    currentTime = (datetime.now(timezone.utc))
    currentTime = currentTime.timestamp()
    myobj = {'name': botname, 'time': currentTime} # formats currenttime in unix timestamp and botname into correct json formatting
    try:
        x = requests.post( webhookmonitorurl, json = myobj) # sends post request
        print("<POST> webhook response is: " + x.text) # log message
        discordremotelog("Goinglivebot/post",14081792,f"webhook response is: {x.text}")
    except Exception as e: # catches exception
        print(f"An exception occurred in main loop: {str(e)}")
        discordremotelog("Goinglivebot/post",10159108,f"An exception occurred in main loop: {str(e)}")
    time.sleep(timeout)