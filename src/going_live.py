import housey_logging
housey_logging.configure()

import logging
import time
from os.path import exists
import os
import config_loader
import discord_webhook_embeds
import embed_file_handler
import twitch_api_handler
import sys
import requests_error_handler

config = config_loader.load_config

discord_webhook_send = discord_webhook_embeds.discord_webhook_send
discord_webhook_edit = discord_webhook_embeds.discord_webhook_edit
discord_webhook_delete = discord_webhook_embeds.discord_webhook_delete
discord_webhook_edit_to_offline = discord_webhook_embeds.discord_webhook_edit_to_offline

save_message_id_to_file = embed_file_handler.save_message_id_to_file
read_message_id_from_file = embed_file_handler.read_message_id_from_file
remove_message_id_file = embed_file_handler.remove_message_id_file

get_token_from_twitch_api = twitch_api_handler.get_token_from_twitch_api
get_stream_json_from_twitch = twitch_api_handler.get_stream_json_from_twitch
get_list_of_team_member_uids = twitch_api_handler.get_list_of_team_member_uids
validate_token = twitch_api_handler.validate_token

handle_request_error = requests_error_handler.handle_request_error

def get_list_of_streamers(list_of_streamers: list, token_from_twitch: str, team_name: str) -> list:

    if not team_name:

        # gets list of streamers from streamers.txt
        if "http" in list_of_streamers:
            get_streamers_trough_request_response = handle_request_error(request_url= list_of_streamers[0])
            list_of_streamers = get_streamers_trough_request_response.text.splitlines()
     
    else:
        list_of_streamers = get_list_of_team_member_uids(team_name, token_from_twitch)

    logging.debug('list of streamers to poll from: %s', list_of_streamers)

    return(list_of_streamers)

# creates embeds folder if not exist allready
def create_embeds_folder():
    os.makedirs("config/embeds", exist_ok=True)
    logging.debug('embed folder was not found so it was created')

def clean_up_old_embeds(entry: dict, i: int):
    for filename in os.listdir(f"config/embeds/{i}"):

        filename = filename.replace(".txt","")
        message_id_from_file,name_from_file, embed_color, username_from_file = read_message_id_from_file(filename, i)

        if entry["use_offline_messages"]:
            discord_webhook_edit_to_offline(message_id_from_file, name_from_file, embed_color, username_from_file, entry)
        elif not entry["leave_messages_untouched"]:
            discord_webhook_delete(message_id_from_file, entry)

        remove_message_id_file(filename, i)

    logging.debug("cleaned up old embeds posted to webhook")

def main():
    
    init_run = True

    logging.info ("starting twitchgoinglive")
    logging.info ("Only errors will be displayed unless otherwise configured")
    
    sys.excepthook = housey_logging.log_exception

    loaded_config, shoutouts = config()
        
    poll_interval_minutes = loaded_config.poll_interval*60

    create_embeds_folder()
    

    token_from_twitch = get_token_from_twitch_api()

    # main loop
    while True:
        
        token_from_twitch = validate_token(token_from_twitch)

        for i, entry in enumerate(shoutouts):

            os.makedirs(f"config/embeds/{i}", exist_ok=True)

            if init_run:
                clean_up_old_embeds(entry, i)
            
            streamers = get_list_of_streamers(entry["streamers"], token_from_twitch, entry["team_name"])

            for streamer in streamers:

                if int(streamer) not in entry["excluded_uids"]:

                    # gets streamer data from twitch api
                    get_stream_json_from_twitch_response, get_stream_json_from_twitch_data, is_live, stream_category,streamer_name = get_stream_json_from_twitch(streamer, token_from_twitch)
                    
                    # if request to twitch api fails requests a new token from twitch and tries again
                    if not get_stream_json_from_twitch_response.ok:
                        token_from_twitch = get_token_from_twitch_api()
                        get_stream_json_from_twitch_response,get_stream_json_from_twitch_data, is_live, stream_category, streamer_name = get_stream_json_from_twitch(streamer, token_from_twitch)
                    
                    # checks if streamer is in allowed categories or if allowed categories is empty
                    if is_live and (stream_category.lower() in entry["allowed_categories"]) or len(entry["allowed_categories"])==0:
                        
                        if stream_category.lower() in entry["allowed_categories"]:
                            logging.debug('%s for %s with name %s is found in allowed categories: %s', stream_category, streamer, streamer_name, entry["allowed_categories"])
                        
                        # updates embed if it allready exsists or creates it if not to discord webhook
                        if exists(f"config/embeds/{str(i)}/{streamer}.txt"):
                            logging.debug('embed allready exsists for %s with name %s, updating it',streamer, streamer_name)
                            message_id_from_file, name_from_file, embed_color, _ = read_message_id_from_file(streamer, i)
                            discord_webhook_edit(get_stream_json_from_twitch_data, message_id_from_file, embed_color, entry)
                        else:
                            logging.debug('no embed exsists for %s with name %s, creating it',streamer, streamer_name)
                            message_id, embed_color, streamer_user_name = discord_webhook_send(get_stream_json_from_twitch_data, entry)
                            save_message_id_to_file(streamer, i, message_id, streamer_name, embed_color, streamer_user_name)
                    
                    else:
                        # removes embed if offline or uses offline message
                        if exists(f"config/embeds/{str(i)}/{streamer}.txt"):
                            logging.debug('%s with name %s is no longer live',streamer, streamer_name)
                            message_id_from_file, name_from_file, embed_color, username_from_file = read_message_id_from_file(streamer, i)
                            
                            if entry["use_offline_messages"]:
                                discord_webhook_edit_to_offline(message_id_from_file, name_from_file, embed_color, username_from_file, entry)
                            elif not entry["leave_messages_untouched"]:
                                discord_webhook_delete(message_id_from_file, entry)
                            remove_message_id_file(streamer, i)
            
        init_run = False

        logging.debug('finished main loop, waiting for %s minutes',loaded_config.poll_interval)
        time.sleep(poll_interval_minutes)

if __name__ == "__main__":
    main()