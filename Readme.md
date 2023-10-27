# what is it
a simple script that polls a list of twitch channels and posts a message to a discord webhook when they are live with a thumbnail and such. updates the message on a predefined schedule and deletes message when the stream goes offline, cleans up all old messages on restart to avoid double posts when the bot crashes.

![Alt text](screenshot.png?raw=true "Title")

included are a local webserver for monitoring purposes and a post script that can talk to a remote monitoring server (both can be disabled by leaving their url entry empty) aswell as a method to post log messages to a discord webhook for remote monitoring.

# how to use
1. make a config folder and place a config.json in the folder
2. in the config add the following code:
```
{
    "twitchClientId": "Twitch api id",
    "twitchSecret": "Twitch api token",
    "webhookurl": "webhook to post main messages to",
    "webhooklogurl": "webhook to post log messages to OPTIONAL",
    "webhookmonitorurl": "url of remote monitoring server OPTIONAL",
    "botname": "bot name to send to remote monitoring server",
    "posttimeout": "timeout in minutes to send message to monitoring server",
    "checktime": time in minutes between polls,
    "hostname": "adress for local webserver",
    "webport": port for local webserver,
}

```
3. create a streamers.txt file and add every streamer you want to poll on a new line
4. run the script

* alternativly you can either build your own docker image with the included dockerfile or use mine with the following command
```
docker run -it -d --name twitchgoinglive -v /path/to/config:/usr/src/app/config keyboardmedic/twitchgoinglive:latest
```

# disclaimer
these scripts are written by an amateur... use at your own risk