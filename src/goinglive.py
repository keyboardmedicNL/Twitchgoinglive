import time
import requests
from os.path import exists
import os
import shutil
import config_loader
import discord_remote_logger
import gotify_error_notifications
import discord_webhook_embeds
import embed_file_handler

# vars
config = config_loader.load_config

discord_remote_log = discord_remote_logger.discord_remote_log
send_gotify_notification = gotify_error_notifications.send_gotify_notification

discord_webhook_send = discord_webhook_embeds.discord_webhook_send
discord_webhook_edit = discord_webhook_embeds.discord_webhook_edit
discord_webhook_delete = discord_webhook_embeds.discord_webhook_delete
discord_webhook_edit_to_offline = discord_webhook_embeds.discord_webhook_edit_to_offline

save_message_id_to_file = embed_file_handler.save_message_id_to_file
read_message_id_from_file = embed_file_handler.read_message_id_from_file
remove_message_id_file = embed_file_handler.remove_message_id_file

# ===== twitch functions =====
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
def get_stream_json_from_twitch(streamer: str) -> tuple[dict, dict, bool, str, str]: 
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

# gets list of streamers to poll
def get_streamers_from_file() -> tuple[list, bool]:
    with open("config/streamers.txt", 'r') as file_with_streamer_ids:
        list_of_streamers = [line.rstrip() for line in file_with_streamer_ids]
        if "http" in list_of_streamers[0]:
            get_streamers_trough_request_response = requests.get(list_of_streamers[0])

            if not get_streamers_trough_request_response.ok:
                print(f"was unable to get list of streamers trough request with response: {get_streamers_trough_request_response}")
                discord_remote_logger("Goinglivebot","red",f"was unable to get list of streamers trough request with response: {get_streamers_trough_request_response}",False)
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
            else:
                list_of_streamers = get_streamers_trough_request_response.text.splitlines()
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
        else:
            is_get_streamers_from_file_succesfull = True

    print(f"list of streamers to poll from: {list_of_streamers}")
    discord_remote_log("Goinglivebot","yellow",f"list of streamers to poll from: {list_of_streamers}",False)

    return(list_of_streamers, is_get_streamers_from_file_succesfull)

#opens file to get auth token
def read_twitch_api_token_from_file() -> str:
    if exists(f"config/token.txt"):
        with open("config/token.txt", 'r') as file_with_twitch_token:
            token_raw = str(file_with_twitch_token.readline())
            twitch_api_token = token_raw.strip()
        print ("Token to use for twitch api auth: " + twitch_api_token)
        discord_remote_log("Goinglivebot","blue","twitch api auth token loaded succesfully",False)
    else:
        twitch_api_token = get_token_from_twitch_api()
        
    return(twitch_api_token)

# creates embeds folder if not exist allready
def create_embeds_folder():
    if not exists("config/embeds"):
        os.makedirs("config/embeds")
        print("embed folder was not found so it was created")
        discord_remote_log("Goinglivebot","blue","embed folder was not found so it was created",False)

# clean op old embeds
def clean_up_old_embeds(list_of_streamers: list ,use_offline_message: bool):
    print("pulling list of streamers once to clean up old messages")
    discord_remote_log("Goinglivebot","yellow","pulling list of streamers once to clean up old messages",False)
    for streamer in list_of_streamers:
        if exists(f"config/embeds/{streamer}.txt"):
            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
            if use_offline_message:
                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
            else:
                discord_webhook_delete(message_id_from_file)
            remove_message_id_file(streamer)
    print("cleaned up old embeds posted to webhook")
    for filename in os.listdir("config/embeds"):
        file_path = os.path.join("config/embeds", filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    print("removed all remaining files in config/embeds/")
    discord_remote_log("Goinglivebot","blue","cleaned up old embeds posted to webhook and cleaned embeds folder",False)

# ===== end of functions =====


# ===== main code =====
loaded_config = config()
create_embeds_folder()
# gets list of streamers once to clean up old embeds, ends script if it fails to get list of streamers
token_from_twitch = read_twitch_api_token_from_file()
streamers, streamer_get_was_succesfull = get_streamers_from_file()

if streamer_get_was_succesfull:
    clean_up_old_embeds(streamers, loaded_config["use_offline_messages"])

    # main loop
    while True:
        try:
            streamers, streamer_get_was_succesfull = get_streamers_from_file()
            if streamer_get_was_succesfull:
                for streamer in streamers:
                    # sets streamer name incase an exception is called before streamer_name is set with a function
                    streamer_name = "unknown"

                    get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                    if not get_stream_json_from_twitch_response.ok:
                        token_from_twitch = get_token_from_twitch_api()
                        get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer)
                    
                    if is_live and (stream_category.lower() in loaded_config["allowed_categories"] or len(loaded_config["allowed_categories"])==0):
                        
                        if stream_category.lower() in loaded_config["allowed_categories"]:
                            print(f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories: {str(loaded_config["allowed_categories"])}")
                            discord_remote_log("Goinglivebot","green",f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories",False)
                        
                        if exists(f"config/embeds/{streamer}.txt"):
                            print(f"embed allready exsists for {streamer} with name {streamer_name}, updating it")
                            discord_remote_log("Goinglivebot","yellow",f"embed allready exsists for {streamer} with name {streamer_name}, updating it",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            discord_webhook_edit(get_stream_json_from_twitch_data,message_id_from_file)
                        else:
                            print(f"no embed exsists for {streamer} with name {streamer_name}, creating it")
                            discord_remote_log("Goinglivebot","yellow",f"no embed exsists for {streamer} with name {streamer_name}, creating it",False)
                            message_id = discord_webhook_send(get_stream_json_from_twitch_data)
                            save_message_id_to_file(streamer,message_id,streamer_name)
                    
                    else:
                        
                        if exists(f"config/embeds/{streamer}.txt"):
                            print(f"{streamer} with name {streamer_name} is no longer live")
                            discord_remote_log("Goinglivebot","yellow",f"{streamer} with name {streamer_name} is no longer live",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            
                            if loaded_config["use_offline_messages"]:
                                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
                            else:
                                discord_webhook_delete(message_id_from_file)
                            remove_message_id_file(streamer)
        
        except Exception as e:
            print(f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}")
            discord_remote_log("Goinglivebot","red",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}",True)
            send_gotify_notification("Clipbot",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}","5")
        
        print(f"finished main loop, waiting for {loaded_config["poll_interval"]} minutes")
        discord_remote_log("Goinglivebot","gray",f"finished main loop, waiting for {loaded_config["poll_interval"]} minutes",False)
        time.sleep(loaded_config["poll_interval"]*60)
else:
    print(f"unable to get streamers from file, stopping script....")