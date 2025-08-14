import config_loader
import logging
import requests_error_handler

loaded_config = config_loader.load_config()

handle_request_error = requests_error_handler.handle_request_error

def get_token_from_twitch_api() -> str:

    logging.info("Requesting new api auth token from twitch")

    get_token_from_twitch_response = handle_request_error(request_type="post",request_url="https://id.twitch.tv/oauth2/token", request_json={"client_id" : str(loaded_config.twitch_api_id), "client_secret" : str(loaded_config.twitch_api_secret), "grant_type":"client_credentials"})
    
    get_token_from_twitch_json = get_token_from_twitch_response.json()
    token_from_twitch = get_token_from_twitch_json["access_token"]
    logging.debug("new twitch api auth token recieved")

    return(token_from_twitch)

def validate_token(token_from_twitch: str) -> str:

    validate_token_response = handle_request_error(request_type="get",status_type_ok=[200,401],request_url="https://id.twitch.tv/oauth2/validate", request_headers={'Authorization':f"Bearer {token_from_twitch}"})

    if validate_token_response.ok:
        logging.debug("validated twitch api token and came back as valid")
        
        return(token_from_twitch)
    
    elif validate_token_response.status_code == 401:
        logging.debug("validated twitch api token and came back as invalid")
        token_from_twitch = get_token_from_twitch_api()

        return(token_from_twitch)

def get_list_of_team_member_uids(team_name: str, api_token: str) -> list:

    logging.info("getting team data from twitch api for team %s", team_name)

    get_team_data_response = handle_request_error(request_type="get",request_url=f"https://api.twitch.tv/helix/teams?name={team_name}", request_headers={'Authorization':f"Bearer {api_token}", 'Client-Id':loaded_config.twitch_api_id})

    team_data_json = get_team_data_response.json()
    list_of_team_users = team_data_json["data"][0]["users"]

    list_of_ids = []

    for user in list_of_team_users:
        list_of_ids.append(user["user_id"])

    return(list_of_ids)

def get_list_of_clips(streamer_id: str, api_token: str, time_last_checked: str) -> list:

    list_of_new_clips = []

    logging.info("getting list of clips from twitch api for streamer %s", streamer_id)

    get_clips_response = handle_request_error(request_type="get",request_url=f"https://api.twitch.tv/helix/clips?broadcaster_id={streamer_id}&started_at={time_last_checked}", request_headers={'Authorization':f"Bearer {api_token}", 'Client-Id':loaded_config.twitch_api_id})

    clips_json = get_clips_response.json()

    for clip in clips_json["data"]:
        list_of_new_clips.append(clip["url"])

    return(list_of_new_clips)

def get_stream_json_from_twitch(streamer: str, token_from_twitch: str) -> tuple[dict, dict, bool, str, str]:

    get_stream_json_from_twitch_response = handle_request_error(request_type="get",request_url=f"https://api.twitch.tv/helix/streams?&user_id={streamer}", request_headers={'Authorization':f"Bearer {token_from_twitch}", 'Client-Id':loaded_config.twitch_api_id})

    get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_response.json()

    try: 

        if str(get_stream_json_from_twitch_request_json["data"][0]["type"]).lower() == "live":

            is_live = True
            stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
            streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]

            logging.info("%s with name %s is live and in category %s",streamer, streamer_name, stream_category)
        
    except:
        is_live = False
        stream_category = ""
        streamer_name = ""

    return(get_stream_json_from_twitch_response, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)


    