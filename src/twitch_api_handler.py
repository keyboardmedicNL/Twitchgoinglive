import config_loader
import discord_remote_logger
import requests
import gotify_error_notifications
from os.path import exists
import logging

# vars

loaded_config = config_loader.load_config()
discord_remote_log = discord_remote_logger.discord_remote_log
send_gotify_notification = gotify_error_notifications.send_gotify_notification


# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        error_count = 0
        while error_count < 4:
            logging.info("Requesting new api auth token from twitch")
            discord_remote_log("Goinglivebot","yellow","Requesting new api auth token from twitch",False)

            get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(loaded_config.twitch_api_id), "client_secret" : str(loaded_config.twitch_api_secret), "grant_type":"client_credentials"})
            
            if get_token_from_twitch_request.ok:
                get_token_from_twitch_json = get_token_from_twitch_request.json()
                token_from_twitch = get_token_from_twitch_json["access_token"]
                logging.debug("new twitch api auth token recieved")
                with open(r'config/token.txt', 'w') as token_file:
                    token_file.write("%s\n" % token_from_twitch)
                break
            else:
                error_count = error_count+1
                logging.error("unable to request new twitch api auth token with response: %s",get_token_from_twitch_request)
                discord_remote_log("Goinglivebot","red",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}",True)
                send_gotify_notification("Clipbot",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}","5")
                token_from_twitch = "empty"
        if error_count == 4:
            raise RuntimeError("Unable to request a new twitch api token after trying 3 times.")
        return(token_from_twitch)

# gets stream information from twitch api
def get_stream_json_from_twitch(streamer: str, token_from_twitch: str) -> tuple[dict, dict, bool, str, str]:
    error_count = 0
    while error_count < 4:
        try:
            get_stream_json_from_twitch_request=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token_from_twitch}", 'Client-Id':loaded_config.twitch_api_id})
            logging.debug("tried to get streamer information for %s with response: %s",streamer, get_stream_json_from_twitch_request)

            get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_request.json()

            stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
            streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]
            if str(get_stream_json_from_twitch_request_json["data"][0]["type"]).lower() == "live":
                is_live = True
                logging.info("%s with name %s is live and in category %s",streamer, streamer_name, stream_category)
                discord_remote_log("Goinglivebot","green",f"{streamer} with name {streamer_name} is live and in category {stream_category}!",False)
            else:
                is_live = False
        except Exception as e:
            discord_remote_log("Goinglivebot","red",f"tried to get streamer information for {streamer} with response: {get_stream_json_from_twitch_request} with exception {e}",True)
            send_gotify_notification("Clipbot",f"tried to get streamer information for {streamer} with response: {get_stream_json_from_twitch_request} with exception {e}","5")
            error_count = error_count +1
    if error_count == 4:
        raise RuntimeError("Unable to get streamer info from twitch after trying 3 times.")

    return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)

#opens file to get auth token
def read_twitch_api_token_from_file() -> str:
    if exists(f"config/token.txt"):
        with open("config/token.txt", 'r') as file_with_twitch_token:
            token_raw = str(file_with_twitch_token.readline())
            twitch_api_token = token_raw.strip()
        logging.debug("Token to use for twitch api loaded")
    else:
        twitch_api_token = get_token_from_twitch_api()
        
    return(twitch_api_token)