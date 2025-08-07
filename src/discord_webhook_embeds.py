import config_loader
import random
import requests
import discord_remote_logger
import gotify_error_notifications
import logging


loaded_config = config_loader.load_config()
discord_remote_log = discord_remote_logger.discord_remote_log
send_gotify_notification = gotify_error_notifications.send_gotify_notification

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
    
    data_to_send_to_webhook = {"content": loaded_config.message_before_embed,"embeds": [
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
    
    send_request_to_discord = requests.post(loaded_config.discord_webhook_url, json=data_to_send_to_webhook, params={'wait': 'true'})
    send_request_to_discord_json = send_request_to_discord.json()
    message_id = send_request_to_discord_json["id"]

    if send_request_to_discord.ok:
        logging.debug("posting message to discord with id: %s for user %s, response is %s",message_id, username, send_request_to_discord)
        discord_remote_log("Goinglivebot","green",f"posting message to discord with discord id: {message_id} for user {username}, response is {send_request_to_discord}",False)
    else:
        logging.error("attempted to post message to discord with id: %s for user %s, response is %s",message_id, username, send_request_to_discord)
        discord_remote_log("Goinglivebot","red",f"attempted to post message to discord with discord id: {message_id} for user {username}, response is {send_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to post message to discord with discord id: {message_id} for user {username}, response is {send_request_to_discord}","5")
        
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
    
    data_to_send_to_webhook = {"content": loaded_config.message_before_embed, "embeds": [
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
    
    edit_request_to_discord = requests.patch(f"{loaded_config.discord_webhook_url}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})
    
    if edit_request_to_discord.ok:
        logging.debug("updating message to discord with id: %s for user %s, response is %s",message_id, username, edit_request_to_discord)
        discord_remote_log("Goinglivebot","green",f"updating message to discord with discord id: {message_id} for user {username}, response is {edit_request_to_discord}",False)
    else:
        logging.error("attempted to update message to discord with id: %s for user %s, response is %s",message_id, username, edit_request_to_discord)
        discord_remote_log("Goinglivebot","red",f"attempted to update message to discord with discord id: {message_id} for user {username}, response is {edit_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update message to discord with discord id: {message_id} for user {username}, response is {edit_request_to_discord}","5")

# deletes discord webhook message
def discord_webhook_delete(message_id: str):
    delete_request_to_discord = requests.delete(f"{loaded_config.discord_webhook_url}/messages/{message_id}", params={'wait': 'true'})
    if delete_request_to_discord.ok:
        logging.debug("deleting message om discord with id: %s, response is %s",message_id, delete_request_to_discord)
        discord_remote_log("Goinglivebot","green",f"deleting message om discord with id: {message_id}, response is {delete_request_to_discord}",False)
    else:
        logging.error("attempted to delete message on discord with id: %s, response is %s",message_id, delete_request_to_discord)
        discord_remote_log("Goinglivebot","red",f"attempted to delete message on discord with id: {message_id}, response is {delete_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to delete message on discord with id: {message_id}, response is {delete_request_to_discord}","5")

# edits currently live embed to offline message
def discord_webhook_edit_to_offline(message_id: str ,filename: str):
    data_to_send_to_webhook = {"content": loaded_config.message_before_embed, "embeds": [
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
    
    edit_to_offline_request_to_discord = requests.patch(f"{loaded_config.discord_webhook_url}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})

    if edit_to_offline_request_to_discord.ok:
        logging.debug("updating to offline message to discord with id: %s for %s, response is %s",message_id, filename, edit_to_offline_request_to_discord)
        discord_remote_log("Goinglivebot","green",f"updating to offline message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}",False)
    else:
        logging.error("attempted to update offline message to discord with id: %s for %s, response is %s",message_id, filename, edit_to_offline_request_to_discord)
        discord_remote_log("Goinglivebot","red",f"attempted to update offlinee message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}",True)
        send_gotify_notification("Clipbot",f"attempted to update offline message to discord with discord id: {message_id} for {filename}, response is {edit_to_offline_request_to_discord}","5")
