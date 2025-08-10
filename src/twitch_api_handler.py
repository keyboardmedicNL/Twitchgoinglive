import config_loader
import requests
import logging
import requests_error_handler
import time

# vars

loaded_config = config_loader.load_config()

init_error_handler = requests_error_handler.init_error_handler
handle_response_not_ok = requests_error_handler.handle_response_not_ok
handle_request_exception = requests_error_handler.handle_request_exception
raise_no_more_tries_exception = requests_error_handler.raise_no_more_tries_exception

# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        
        time_before_retry, max_errors_allowed, error_count = init_error_handler()
        
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
                    error_count, remaining_errors = handle_response_not_ok(error_count)
                    logging.error("unable to request new twitch api auth token with response: %s trying %s more times and waiting for %s seconds",get_token_from_twitch_request, remaining_errors , time_before_retry)
                    if error_count != max_errors_allowed:
                        time.sleep(time_before_retry)

            except Exception as e:
                    error_count, remaining_errors = handle_request_exception(error_count)
                    logging.error("unable to request new twitch api auth token with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                    if error_count != max_errors_allowed:
                        time.sleep(time_before_retry)

        if error_count == max_errors_allowed:
            raise_no_more_tries_exception(max_errors_allowed)

# gets stream information from twitch api
def get_stream_json_from_twitch(streamer: str, token_from_twitch: str) -> tuple[dict, dict, bool, str, str]:

    time_before_retry, max_errors_allowed, error_count = init_error_handler()
        
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
                    
                except:
                    is_live = False
                    stream_category = ""
                    streamer_name = ""

                return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)

            else:
                error_count, remaining_errors = handle_response_not_ok(error_count)
                logging.error("tried to get streamer information for %s with response: %s trying %s more times and waiting for %s seconds",streamer, get_stream_json_from_twitch_request, remaining_errors, time_before_retry)
                if error_count != max_errors_allowed:
                    time.sleep(time_before_retry)

        except Exception as e:
            error_count, remaining_errors = handle_request_exception(error_count)
            logging.error("tried to get streamer information for %s with exception: %s trying %s more times and waiting for %s seconds",streamer, e, remaining_errors , time_before_retry)
            if error_count != max_errors_allowed:
                time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
         raise_no_more_tries_exception(max_errors_allowed)

# get list of team member uids
def get_list_of_team_member_uids(team_name: str, api_token: str) -> list:

    time_before_retry, max_errors_allowed, error_count = init_error_handler()
        
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
                error_count, remaining_errors = handle_response_not_ok(error_count)
                logging.error("unable to request team data from twitch with response: %s trying %s more times and waiting for %s seconds",get_team_data_response, remaining_errors , time_before_retry)
                if error_count != max_errors_allowed:
                    time.sleep(time_before_retry)

        except Exception as e:
                error_count, remaining_errors = handle_request_exception(error_count)
                logging.error("unable to request team data from twitch with exception: %s trying %s more times and waiting for %s seconds", e, remaining_errors, time_before_retry)
                if error_count != max_errors_allowed:
                    time.sleep(time_before_retry)

    if error_count == max_errors_allowed:
        raise_no_more_tries_exception(max_errors_allowed)
    