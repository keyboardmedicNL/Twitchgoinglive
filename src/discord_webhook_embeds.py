import config_loader
import random
import logging
import requests_error_handler
import color_picker
import sky_bass_functions

loaded_config = config_loader.load_config()

handle_request_error = requests_error_handler.handle_request_error

pick_random_color = color_picker.pick_random_color

sanitize_username = sky_bass_functions.sanitize_streamer_username

def parse_data_for_webhook(streamer_data: dict, color: str) -> tuple[dict, str]:

    username = streamer_data["data"][0]["user_name"]
    user = streamer_data["data"][0]["user_login"]
    title = streamer_data["data"][0]["title"]
    game = streamer_data["data"][0]["game_name"]
    viewers = streamer_data["data"][0]["viewer_count"]
    started = streamer_data["data"][0]["started_at"]
    thumbnail = streamer_data["data"][0]["thumbnail_url"]

    if streamer_data["data"][0]["game_name"] == "":
        game = "none"

    if loaded_config.use_skybass:
        username = sanitize_username(username, loaded_config.names_to_ignore)

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

def parse_username_for_embed(username: str) -> str:

    message_before_embed = loaded_config.message_before_embed

    if "<username>" in message_before_embed:
        message_with_username = message_before_embed.replace("<username>", username)

    else:
        message_with_username = message_before_embed
    
    return(message_with_username)

def discord_webhook_send(streamer_data: dict ) -> tuple[str ,str, str]:

    color = str(pick_random_color("decimal"))
    
    data_to_send_to_webhook, username = parse_data_for_webhook(streamer_data, color)

    send_request_to_discord = handle_request_error(request_type= "post", request_url= loaded_config.discord_webhook_url, request_json= data_to_send_to_webhook, request_params= {'wait': 'true'})

    send_request_to_discord_json = send_request_to_discord.json()
    message_id = send_request_to_discord_json["id"]

    logging.debug("posting message to discord with id: %s for user %s, response is %s",message_id, username, send_request_to_discord)

    return(message_id, color, username)
    
def discord_webhook_edit(streamer_data: dict,message_id: str, embed_color: str):

    data_to_send_to_webhook, username = parse_data_for_webhook(streamer_data, embed_color)
    
    if loaded_config.allow_failure:
        status_types_to_pass = [200,404]
    else:
        status_types_to_pass = [200]

    edit_request_to_discord = handle_request_error(status_type_ok=status_types_to_pass, request_type="patch", request_url= f"{loaded_config.discord_webhook_url}/messages/{message_id}", request_json= data_to_send_to_webhook, request_params= {'wait': 'true'})
    
    logging.debug("updating message to discord with id: %s for user %s, response is %s",message_id, username, edit_request_to_discord)

def discord_webhook_delete(message_id: str):

    if loaded_config.allow_failure:
        status_types_to_pass = [204,404]
    else:
        status_types_to_pass = [204]

    delete_request_to_discord = handle_request_error(status_type_ok=status_types_to_pass ,request_type="delete", request_url= f"{loaded_config.discord_webhook_url}/messages/{message_id}", request_params= {'wait': 'true'})
    
    logging.debug("deleting message om discord with id: %s, response is %s",message_id, delete_request_to_discord)

def discord_webhook_edit_to_offline(message_id: str ,filename: str, embed_color: str, username: str):

    message_before_embed = parse_username_for_embed(username)

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
    
    edit_to_offline_request_to_discord = handle_request_error(request_type="patch", request_url= f"{loaded_config.discord_webhook_url}/messages/{message_id}", request_json= data_to_send_to_webhook, request_params= {'wait': 'true'})

    logging.debug("updating to offline message to discord with id: %s for %s, response is %s",message_id, filename, edit_to_offline_request_to_discord)