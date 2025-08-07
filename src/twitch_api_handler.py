import config_loader
import requests
from os.path import exists
import logging

# vars

loaded_config = config_loader.load_config()


# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        error_count = 0
        while error_count < 4:
            logging.info("Requesting new api auth token from twitch")

            get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(loaded_config.twitch_api_id), "client_secret" : str(loaded_config.twitch_api_secret), "grant_type":"client_credentials"})
            
            if get_token_from_twitch_request.ok:
                get_token_from_twitch_json = get_token_from_twitch_request.json()
                token_from_twitch = get_token_from_twitch_json["access_token"]
                logging.debug("new twitch api auth token recieved")
                with open(r'config/token.txt', 'w') as token_file:
                    token_file.write("%s\n" % token_from_twitch)

                break

            else:
                logging.error("unable to request new twitch api auth token with response: %s",get_token_from_twitch_request)
                error_count = error_count+1
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

            if get_stream_json_from_twitch_request.ok:
                get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_request.json()

                try:               
                    if str(get_stream_json_from_twitch_request_json["data"][0]["type"]).lower() == "live":
                        is_live = True
                        stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
                        streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]
                        logging.info("%s with name %s is live and in category %s",streamer, streamer_name, stream_category)
                    break
                except:
                    is_live = False
                    stream_category = ""
                    streamer_name = ""
                    break
            else:
                error_count = error_count+1
                logging.error("tried to get streamer information for %s with response: %s",streamer, get_stream_json_from_twitch_request)

        except Exception as e:
            logging.error("tried to get streamer information for %s with response: %s with exception: %s",streamer, get_stream_json_from_twitch_request, e)
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