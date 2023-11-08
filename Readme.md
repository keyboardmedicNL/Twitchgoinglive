# important
the config format has changed between version 0.1.1 and 0.2, ensure you use the new config format or the script will not work!

# what is it
a simple script that polls a list of twitch channels and posts a message to a discord webhook when they are live with a thumbnail and such. updates the message on a predefined schedule and deletes message when the stream goes offline, cleans up all old messages on restart to avoid double posts when the bot crashes.

![Alt text](screenshot.png?raw=true "Title")

**the script currently comes with 2 versions:**   
- the lite version, wich just contains the script to check for livestreams and posts them to discord aswell.    
- the full version, wich contains the script, the option to send log messages to a discord webhook for easy remote monitoring and a simple webserver that can be pinged to monitor uptime, aswell as simple service that will send a http post to an adress of your chosing with a configurable timer with the json ```{'name': "bot_name", 'time': "unix timestamp of current time in utc"}``` all of this can be toggled on or off in the config


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
    "post_interval": "timeout in minutes to send message to monitoring server OPTIONAL"
}
```
5. create a streamers.txt file in the config folder and add the username of every streamer you want to poll on a new line, alternativly add a url to a txt file that contains the list to poll
```
keyboardmedic
dj_acidion
backupiboh
```
6. run the script:   
on windows: with the included start.bat file for your version  
on linux: in a terminal with ```python goinglive.py``` or ```python goinglivelite.py```

* alternativly you can either build your own docker image with the included dockerfile or use mine with the following command (note: the docker version runs the full version and thus requires the full config)
```
docker run -it -d --name twitchgoinglive -v /path/to/config:/usr/src/app/config keyboardmedic/twitchgoinglive:latest
```

# disclaimer
these scripts are written by an amateur... use at your own risk
