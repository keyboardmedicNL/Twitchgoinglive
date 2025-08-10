import config_loader
import random
import requests
import logging
import time

loaded_config = config_loader.load_config()
time_before_retry = 60
max_errors_allowed = 3

def parse_data_for_webhook(streamer_data: dict, color: str) -> tuple[dict, str]:

    username, user, title, game, viewers, started, thumbnail = parse_streamer_data(streamer_data)

    message_before_embed = parse_username_for_embed(username)

    data_to_send_to_webhook = {"content": message_before_embed,"embeds": [
                    {
                    "title": f":red_circle: {username} is now live!",
                    "description": title,
                    "url": f"https://www.twitch.tv/{user}",
                    "color": color,
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
    
    return(data_to_send_to_webhook, username)

def parse_streamer_data(streamer_data: dict) -> tuple[str, str, str, str, str, str, str]:
    
    username = streamer_data["data"][0]["user_name"]
    user = streamer_data["data"][0]["user_login"]
    title = streamer_data["data"][0]["title"]
    game = streamer_data["data"][0]["game_name"]
    viewers = streamer_data["data"][0]["viewer_count"]
    started = streamer_data["data"][0]["started_at"]
    thumbnail = streamer_data["data"][0]["thumbnail_url"]

    if streamer_data["data"][0]["game_name"] == "":
        game = "none"

    return(username, user, title, game, viewers, started, thumbnail)

def parse_username_for_embed(username: str) -> str:

    message_before_embed = loaded_config.message_before_embed

    if "<username>" in message_before_embed:
        message_with_username = message_before_embed.replace("<username>", username)

    else:
        message_with_username = message_before_embed
    
    return(message_with_username)

def random_color_generator() -> str:

    rgb_list = []

    for index in range(3):
        color = random.randint(0,255)
        rgb_list.append(color)

    color_decimal = int(rgb_list[0]) * 65536 + int(rgb_list[1]) * 256 + int(rgb_list[2])
    color_decimal_string = str(color_decimal)

    return(color_decimal_string)

def discord_webhook_send(streamer_data: dict ) -> tuple[str ,str, str]:
    error_count = 0
    while error_count < max_errors_allowed:

        try:

            color = random_color_generator()
            
            data_to_send_to_webhook, username = parse_data_for_webhook(streamer_data, color)

            send_request_to_discord = requests.post(loaded_config.discord_webhook_url, json=data_to_send_to_webhook, params={'wait': 'true'})
            send_request_to_discord_json = send_request_to_discord.json()
            message_id = send_request_to_discord_json["id"]

            if send_request_to_discord.ok:
                logging.debug("posting message to discord with id: %s for user %s, response is %s",message_id, username, send_request_to_discord)
                break
            else:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("tried posting message to discord with id: %s for user %s, response is %s trying %s more times and waiting for %s seconds",message_id, username, send_request_to_discord, remaining_errors , time_before_retry)
                    time.sleep(time_before_retry)
                    
        except Exception as e:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("attempted to post message to discord with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                    time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("tried to create new webhook message on discord 3 times and failed")       
    return(message_id, color, username)

def discord_webhook_edit(streamer_data: dict,message_id: str, embed_color: str):
    error_count = 0
    while error_count < max_errors_allowed:
        try:

            data_to_send_to_webhook, username = parse_data_for_webhook(streamer_data, embed_color)
            
            edit_request_to_discord = requests.patch(f"{loaded_config.discord_webhook_url}/messages/{message_id}", json=data_to_send_to_webhook, params={'wait': 'true'})
            
            if edit_request_to_discord.ok:
                logging.debug("updating message to discord with id: %s for user %s, response is %s",message_id, username, edit_request_to_discord)
                break
            else:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("tried updating message to discord with id: %s for user %s, response is %s trying %s more times and waiting for %s seconds",message_id, username, edit_request_to_discord, remaining_errors,  time_before_retry)
                    time.sleep(time_before_retry)

        except Exception as e:
            error_count = error_count+1
            remaining_errors = max_errors_allowed-error_count

            if not error_count == max_errors_allowed:
                logging.error("attempted to update message to discord with exception: %e trying %s more times and waiting for %s seconds", e, remaining_errors,  time_before_retry)
                time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("tried to update discord webhook message 3 times and failed")

def discord_webhook_delete(message_id: str):

    error_count = 0
    while error_count < max_errors_allowed:

        try:

            delete_request_to_discord = requests.delete(f"{loaded_config.discord_webhook_url}/messages/{message_id}", params={'wait': 'true'})
            
            if delete_request_to_discord.ok:
                logging.debug("deleting message om discord with id: %s, response is %s",message_id, delete_request_to_discord)
                break
            
            else:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("tried deleting message om discord with id: %s, response is %s trying %s more times and waiting for %s seconds",message_id, delete_request_to_discord, remaining_errors, time_before_retry)
                    time.sleep(time_before_retry)

        except Exception as e:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("attempted to delete message on discord with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                    time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("tried to delete discord webhook message 3 times and failed")

def discord_webhook_edit_to_offline(message_id: str ,filename: str, embed_color: str, username: str):

    error_count = 0
    while error_count < max_errors_allowed:
        
        message_before_embed = parse_username_for_embed(username)

        try:
            data_to_send_to_webhook = {"content": message_before_embed, "embeds": [
                    {
                    "title": f":x: {filename} has gone offline!",
                    "description": "",
                    "url": f"https://www.twitch.tv/{filename.lower()}",
                    "color": embed_color,
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
                break
            else:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("tried updating to offline message to discord with id: %s for %s, response is %s trying %s more times and waiting for %s seconds",message_id, filename, edit_to_offline_request_to_discord, remaining_errors, time_before_retry)    
                    time.sleep(time_before_retry)  

        except Exception as e:
            error_count = error_count+1
            remaining_errors = max_errors_allowed-error_count

            if not error_count == max_errors_allowed:
                logging.error("attempted to update offline message to discord with exception %e trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("tried to edit discord webhook message to offline 3 times and failed")
