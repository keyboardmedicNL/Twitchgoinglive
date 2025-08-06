import config_loader
import discord_remote_logger
import requests
import gotify_error_notifications


# vars
loaded_config = config_loader.load_config()
discord_remote_log = discord_remote_logger.discord_remote_log
send_gotify_notification = gotify_error_notifications.send_gotify_notification


# renews token used for twitch api calls
def get_token_from_twitch_api() -> str:
        if loaded_config["verbose"] >= 1: 
            print("Requesting new api auth token from twitch")
            discord_remote_log("Goinglivebot","yellow","Requesting new api auth token from twitch",False)

        get_token_from_twitch_request=requests.post("https://id.twitch.tv/oauth2/token", json={"client_id" : str(loaded_config["twitch_api_id"]), "client_secret" : str(loaded_config["twitch_api_secret"]), "grant_type":"client_credentials"})
        
        if get_token_from_twitch_request.ok:
            get_token_from_twitch_json = get_token_from_twitch_request.json()
            token_from_twitch = get_token_from_twitch_json["access_token"]
            if loaded_config["verbose"] >= 1:
                print(f"new twitch api auth token is: {token_from_twitch}")
                discord_remote_log("Goinglivebot","green",f"new twitch api auth token recieved",False)
            with open(r'config/token.txt', 'w') as token_file:
                token_file.write("%s\n" % token_from_twitch)
        else:
            print(f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}")
            discord_remote_log("Goinglivebot","red",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}",True)
            send_gotify_notification("Clipbot",f"unable to request new twitch api auth token with response: {get_token_from_twitch_request}","5")
            token_from_twitch = "empty"
        return(token_from_twitch)

# gets stream information from twitch api
def get_stream_json_from_twitch(streamer: str, token_from_twitch: str) -> tuple[dict, dict, bool, str, str]: 
    get_stream_json_from_twitch_request=requests.get(f"https://api.twitch.tv/helix/streams?&user_id={streamer}", headers={'Authorization':f"Bearer {token_from_twitch}", 'Client-Id':loaded_config["twitch_api_id"]})
    print(f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}")

    if get_stream_json_from_twitch_request.ok:
        if loaded_config["verbose"] >= 1:
            discord_remote_log("Goinglivebot","green",f"got streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",False) 
    else:
            discord_remote_log("Goinglivebot","red",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}",True)
            send_gotify_notification("Clipbot",f"tried to get streamer information with function get_stream_json_from_twitch for {streamer} with response: {get_stream_json_from_twitch_request}","5")

    get_stream_json_from_twitch_request_json = get_stream_json_from_twitch_request.json()

    try:
        if str(get_stream_json_from_twitch_request_json["data"][0]["type"]).lower() == "live":
            is_live = True
        else:
            is_live = False
        stream_category = get_stream_json_from_twitch_request_json["data"][0]["game_name"]
        streamer_name = get_stream_json_from_twitch_request_json["data"][0]["user_name"]
        print(f"{streamer} with name {streamer_name} is live and in category {stream_category}!")
        discord_remote_log("Goinglivebot","green",f"{streamer} with name {streamer_name} is live and in category {stream_category}!",False)
    except:
        is_live = False
        stream_category = ""
        streamer_name = ""

    return(get_stream_json_from_twitch_request, get_stream_json_from_twitch_request_json, is_live, stream_category, streamer_name)