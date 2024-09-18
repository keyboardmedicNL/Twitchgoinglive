# Download the script from releases do NOT just clone the repo
please...

# important
the config format has changed between version 0.1.1 and 0.2, ensure you use the new config format or the script will not work!

# what is it
a simple script that polls a list of twitch channels and posts a message to a discord webhook when they are live with a thumbnail and such. updates the message on a predefined schedule and deletes message when the stream goes offline, cleans up all old messages on restart to avoid double posts when the bot crashes.

![Alt text](screenshot.png?raw=true "Title")

**the script currently comes with 2 versions:**   
- the lite version, wich just contains the script to check for livestreams and posts them to discord aswell.    
- the full version, wich contains the script, the option to send log messages to a discord webhook for easy remote monitoring and a simple webserver that can be pinged to monitor uptime, aswell as simple remote post service that will send a http post to an adress of your chosing with a configurable timer with the json ```{'name': "bot_name", 'time': "unix timestamp of current time in utc"}``` and the option to send error messages to a gotify server, all of this can be toggled on or off in the config


# how to use
1. install python on your system from the python website https://www.python.org/downloads/ (if you want to use the included batch to launch be sure to select ```add python to path``` during the installation)
2. in the config folder, copy the ```example_config.json``` and rename it to ```config.json```
3. you will need a twitch api id and secret. If you do not have one you can register an application at https://dev.twitch.tv/ to obtain your id and secret
3. in the config adjust the following lines as needed for your version:   

lite:
```
{
    "twitch_api_id": "Twitch api id",
    "twitch_api_secret": "Twitch api token",
    "discord_webhook_url": "webhook to post main messages to",
    "poll_interval": time in minutes between polls,
}
```

full:
```
{
    "twitch_api_id": "Twitch api id",
    "twitch_api_secret": "Twitch api token",
    "discord_webhook_url": "webhook to post main messages to",
    "poll_interval": "time in minutes between polls",
    "use_web_server": "true or false",
    "web_server_url": "adress for local webserver OPTIONAL",
    "web_server_port": "port for local webserver OPTIONAL",
    "use_discord_logs": "true or false",
    "discord_remote_log_url": "webhook to post log messages to OPTIONAL",
    "use_remote_post": "true or false",
    "remote_http_server_url": "url of remote monitoring server OPTIONAL",
    "bot_name": "bot name to send to remote monitoring server OPTIONAL",
    "post_interval": "timeout in minutes to send message to monitoring server OPTIONAL",
    "pingid": "user or group id to ping incase of an error for remote logging OPTIONAL"
    "verbose": "true or false, wether or not the script outputs all logging messages or just the basics",
    "use_gotify": "true or false",
    "gotifyurl": "url for your gotify server"
}
```
5. create a streamers.txt file in the config folder and add the user id of every streamer you want to poll on a new line, alternativly add a url to a txt file that contains the list to poll (if you dont have the user id you can use https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/ to get the id from the twitch api, alternativly there is a included getuserid.py script you can run in a terminal to get it yourself from the api)
```
123456
234567
345678
```
6. run the script:   
on windows: with the included start.bat file for your version  
on linux: in a terminal with ```python goinglive.py``` or ```python goinglivelite.py```

* alternativly you can either build your own docker image with the included dockerfile or use mine with the following command (note: the docker version runs the full version and thus requires the full config)
```
docker run -it -d --name twitchgoinglive -v /path/to/config:/usr/src/app/config keyboardmedic/twitchgoinglive:latest
```
# how it works
**main script**
- loads the config.   
- launches the webserver and post server in seperate threads if selected in the config.
- checks if token.txt is present in the config folder and reads it to load the auth token for twitch api calls, if not it runs the get_token function to request an auth token from twitch and saves it to token.txt
- it gets the list of streamers to poll with the get_streamers function and checks if any txt files exsist in the config folder with streamer names with a saved messageid, if it finds any it will attempt to delete the messages on discord with the corresponding message id, it does this to avoid leaving old messages up between restarts
- it then loops trough all the streamers and gets the stream information from the twitch api to see if they are live and to retrieve the needed data for the message
- if a streamer is live it checks if a txt file with the streamers name exsists, if it does not exsist it posts a message to discord and creates a txt file with the name of the streamer wich holds the messageid of the message posted to discord, if the txt does exsist it reads it for the messageid and then updates the message on discord with that id
- if a streamer is not live it checks if a txt file exsists with the streamers name and if it does it will read it for the message id and delete that message on discord.
- it then waits for the preconfigured time and loops back to looping trough the streamers.

**webserver**
- loads the config
- serves a website on the defined adress with the defined port with just a plain text message that says "hello i am a webserver"

**remote post**
- loads the config
- sends a http post to the configured adress with the following json ```{'name': "bot_name as configured", 'time': "unix timestamp of current time in utc"}```
- waits for the configured timeout and then sends a post again

**gotify**
- if an error occurs a message gets pushed to your gotify server

# disclaimer
these scripts are written by an amateur... use at your own risk
