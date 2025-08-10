import config_loader
import requests
from os.path import exists
import logging
import time

# vars

loaded_config = config_loader.load_config()
time_before_retry = 60
max_errors_allowed = 3

# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        
        error_count = 0

        while error_count < max_errors_allowed:

            try:
                logging.info("Requesting new api auth token from twitch")

                get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(loaded_config.twitch_api_id), "client_secret" : str(loaded_config.twitch_api_secret), "grant_type":"client_credentials"})
                
                if get_token_from_twitch_request.ok:

                    get_token_from_twitch_json = get_token_from_twitch_request.json()
                    token_from_twitch = get_token_from_twitch_json["access_token"]
                    logging.debug("new twitch api auth token recieved")

                    return(token_from_twitch)

                else:
                    error_count = error_count+1
                    remaining_errors = max_errors_allowed-error_count

                    if not error_count == max_errors_allowed:
                        logging.error("unable to request new twitch api auth token with response: %s trying %s more times and waiting for %s seconds",get_token_from_twitch_request, remaining_errors , time_before_retry)
                        time.sleep(time_before_retry)

            except Exception as e:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("unable to request new twitch api auth token with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                    time.sleep(time_before_retry)

        if error_count == max_errors_allowed:
            raise RuntimeError("Unable to request a new twitch api token after trying 3 times.")
        

# gets stream information from twitch api
def get_stream_json_from_twitch(streamer: str, token_from_twitch: str) -> tuple[dict, dict, bool, str, str]:

    error_count = 0

    while error_count < max_errors_allowed:
        
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
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("tried to get streamer information for %s with response: %s trying %s more times and waiting for %s seconds",streamer, get_stream_json_from_twitch_request, remaining_errors, time_before_retry)
                    time.sleep(time_before_retry)

        except Exception as e:
            error_count = error_count+1
            remaining_errors = max_errors_allowed-error_count

            if not error_count == max_errors_allowed:
                logging.error("tried to get streamer information for %s with exception: %s trying %s more times and waiting for %s seconds",streamer, e, remaining_errors , time_before_retry)
                time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("Unable to get streamer info from twitch after trying 3 times.")

    return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)

# get list of team member uids
def get_list_of_team_member_uids(team_name: str, api_token: str) -> list:

    error_count = 0
    while error_count < max_errors_allowed:

        try:
            logging.info("getting team data from twitch api for team %s", team_name)

            get_team_data_response = requests.get(f"https://api.twitch.tv/helix/teams?name={team_name}", headers={'Authorization':f"Bearer {api_token}", 'Client-Id':loaded_config.twitch_api_id})

            if get_team_data_response.ok:
                team_data_json = get_team_data_response.json()
                list_of_team_users = team_data_json["data"][0]["users"]

                list_of_ids = []

                for user in list_of_team_users:
                    list_of_ids.append(user["user_id"])

                return(list_of_ids)

            else:
                error_count = error_count+1
                remaining_errors = max_errors_allowed-error_count

                if not error_count == max_errors_allowed:
                    logging.error("unable to request team data from twitch with response: %s trying %s more times and waiting for %s seconds",get_team_data_response, remaining_errors , time_before_retry)
                    time.sleep(time_before_retry)

        except Exception as e:
            error_count = error_count+1
            remaining_errors = max_errors_allowed-error_count

            if not error_count == max_errors_allowed:
                logging.error("unable to request team data from twitch with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise RuntimeError("Unable to request team data from after trying 3 times.")
