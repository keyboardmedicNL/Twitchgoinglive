# Download the script from releases do NOT just clone the repo
please...

# important
I have completely refactored the script, it now uses yaml instead of json for the config and i have removed a bunch of unneeded code. please start with a new config if your updating... the 2 different versions have been condenses to 1 simpler version, the last update converts your old config to the new format automaticly on first run, your old config will be saved as config.old.yaml

# what is it
a simple script that polls a list of twitch channels and posts a message to a discord webhook when they are live with a thumbnail and such. updates the message on a predefined schedule and deletes message when the stream goes offline or changes it to an offline message, cleans up all old messages on restart to avoid double posts when the bot crashes. it can now handle multiple discord webhooks in a single instance!

![Alt text](screenshot.png?raw=true "Title")

![Alt text](screenshot_offline.png?raw=true "Title")


# how to use
1. install python on your system from the python website https://www.python.org/downloads/ (if you want to use the included batch to launch be sure to select ```add python to path``` during the installation)
2. in the config folder, copy the ```example_config.yaml``` and rename it to ```config.yaml```
3. you will need a twitch api id and secret. If you do not have one you can register an application at https://dev.twitch.tv/ to obtain your id and secret
3. in the config adjust the required lines and uncomment and adjust any optional lines you want to change:   

```
# REQUIRED PARAMETERS
twitch_api_id: YOUR_API_ID # your twitch api id
twitch_api_secret: YOUR_API_SECRET # your twitch api secret

# OPTIONAL PARAMETERS

#poll_interval: 10 # time in minutes on how often the script should check if anyone is live DEFAULT: 10 minutes
#max_errors_allowed: 3 # the amount of times the bot will retry a http request when it runs into an error performing it
#time_before_retry: 60 # time in seconds between retry attempts for errored out http requests
#allow_failure: true or false # allows manual deletion of messages without causing an exception unless use_offline_messages is also used, Leaving this off will provide better error handling

# REQUIRED PARAMETERS

shoutouts:

  # first discord webhook to handle
- discord_webhook_url: your_webhook_url
  streamers: # list of streamers uuid's to check, can be a list of integers OR a link to a file containing the uuids with a new entry on each line
  - 123456789 # streamers uuid
  - https://link_to_your_list_of_streamers_file/ #link to a raw file with a list of streamer uuid's

  # OPTIONAL PARAMETERS

  #message_before_embed: this is a message that shows above the embed # a custom message to show above the going live embed message, add <username> in the string to add the streamers name to the message. Can be used to ping roles or users DEFAULT ""
  
  #use_offline_messages: false # wether or not the bot should delete the message when someone goes offline or should display an offline message instead DEFAULT false
  #leave_messages_untouched: false #copies streamcords default behaviour where after a user goes offline the message remains as it did when they were last live
  
  #team_name: YOUR_TEAM_NAME # add the name of a twitch team to use the list of members in a twitch team to check instead of streamers the streamers list
  
  #excluded_uids: # list of uids to exclude from the bot, usefull if you poll an entire team and want to leave out certain members of team
  # - 123456
  # - 234567
  
  #allowed_categories: # a list of allowed categories your streamers need to be in for the bot to show a going live message DEFAULT all categories allowed
  #- djs
  #- music
  
  # sky bass functions: a set of slightly obscure entries used in slightly obscure functions for use on the sky bass discord
  #use_skybass: true # enables use of functions specificly written for the sky bass discord 
  #names_to_ignore: # list of dicts of usernames to ignore for filtering by sky bass functions that remove dnb, dj, vox or music from the username for embed message
  #- name: "ApocDnB"
  #  replace_with: "Zach and Apoc"
  #  message: "this message will replace the message define in message_before_embed for this user"
  #- name: "dj_Acidion"
  #  replace_with: "Acidman"
  #  message: "this message will replace the message define in message_before_embed for this user" 


  # second discord webhook to handle
#- discord_webhook_url: your_webhook_url
#  streamers:
#  - 123456789
#  - 2345678910
```

5. install the dependencies in the requirements.txt, ideally you use a virtual enviroment for this... to do so
    1. on linux python-venv is a seperate package and needs to be installed first.
    2. in the root of this project run ```python3 -m venv .env``` then use ```source .env/bin/active``` to activate your virtual enviroment
    3. you can now install the dependencies with ```pip install -r requirements```

6. run the script:   
on windows: with the included start.bat file
on linux: in a terminal with ```python src/going_live.py```

# docker
alternativly you can either build your own docker image with the included dockerfile or use mine with the following command
```
docker run -it -d --name twitchgoinglive -v /path/to/config:/usr/src/app/config keyboardmedic/twitchgoinglive:latest
```
to run the build in getuserid.py script from a docker container you can open a shell into the container with the following command   
``` 
docker exec -it twitchgoinglive sh
```
and then you excecute the script with the command   
```
python src/get_user_id.py
```
to exit out of the shell press crtl+p followed by ctrl+q to escape from the shell

or using docker compose:
```
name: twitchgoinglive

services:
    twitchgoinglive:
        image: keyboardmedic/twitchgoinglive:latest
        volumes:
         - /path/to/your/config/folder:/usr/src/app/config
```

# FAQ

### the bot crashed after i deleted a message from discord
The bot expects to be able to manipulate the messages it created, if they no longer exsist the bot will try to change or delete the message a set amount of times and then crash.

To fix: go to your bots config folder and delete all files in config/embeds, delete all exsisting messages in discord and restart the bot

OR

Use the config entry: allow_failure: true to allow manual message deletion without causing errors

### if i put @everyone into the message_before_embed entry in the config the bot crashes
@ is used by yaml for other things, enclose the message in qoutes or double qoutes to fix

example
```
message_before_embed: "@everyone im live!"
```

# disclaimer
Scripts are written by an amateur, use at your own risk

the only vibe used in this code is background drum and bass
