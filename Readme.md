# Download the script from releases do NOT just clone the repo
please...

# important
I have completely refactored the script, it now uses yaml instead of json for the config and i have removed a bunch of unneeded code. please start with a new config if your updating... the 2 different versions have been condenses to 1 simpler version

# what is it
a simple script that polls a list of twitch channels and posts a message to a discord webhook when they are live with a thumbnail and such. updates the message on a predefined schedule and deletes message when the stream goes offline or changes it to an offline message, cleans up all old messages on restart to avoid double posts when the bot crashes.

![Alt text](screenshot.png?raw=true "Title")

![Alt text](screenshot_offline.png?raw=true "Title")


# how to use
1. install python on your system from the python website https://www.python.org/downloads/ (if you want to use the included batch to launch be sure to select ```add python to path``` during the installation)
2. in the config folder, copy the ```example_config.yaml``` and rename it to ```config.yaml```
3. you will need a twitch api id and secret. If you do not have one you can register an application at https://dev.twitch.tv/ to obtain your id and secret
3. in the config adjust the required lines and uncomment and adjust any optional lines you want to change:   

```
# REQUIRED PARAMETERS
# REQUIRED PARAMETERS
twitch_api_id: YOUR_API_ID # your twitch api id
twitch_api_secret: YOUR_API_SECRET # your twitch api secret
discord_webhook_url: YOUR_WEBHOOK_URL # webhook url from discord to post going live messages to

# everything below this is optional, uncomment the line (remove the #) if you want to use it
#poll_interval: 10 # time in minutes on how often the script should check if anyone is live DEFAULT: 10 minutes
#allowed_categories: # a list of allowed categories your streamers need to be in for the bot to show a going live message DEFAULT all categories allowed
#- djs
#- music
#message_before_embed: this is a message that shows above the embed # a custom message to show above the going live embed message, add <username> in the string to add the streamers name to the message. Can be used to ping roles or users DEFAULT ""
#use_offline_messages: false # wether or not the bot should delete the message when someone goes offline or should display an offline message instead DEFAULT false
#team_name: YOUR_TEAM_NAME # add the name of a twitch team to use the list of members in a twitch team to check instead of streamers.txt
#excluded_uids: # list of uids to exclude from the bot, usefull if you poll an entire team and want to leave out certain members of team
# - 123456
# - 234567

# sky bass functions: a set of slightly obscure entries used in slightly obscure functions for use on the sky bass discord
#use_skybass: true # enables use of functions specificly written for the sky bass discord
#names_to_ignore: # list of dicts of usernames to ignore for filtering by sky bass functions that remove dnb, dj, vox or music from the username for embed message
#- name: "ApocDnB"
#  replace_with: "Zach and Apoc"
#- name: "dj_Acidion"
#  replace_with: "Acidman"
```

5. create a streamers.txt file in the config folder and add the user id of every streamer you want to poll on a new line, alternativly add a url to a txt file that contains the list to poll (if you dont have the user id you can use https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/ to get the id from the twitch api, alternativly there is a included getuserid.py script you can run in a terminal to get it yourself from the api)
```
123456
234567
345678
```
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

# disclaimer
these scripts are written by an amateur... use at your own risk
