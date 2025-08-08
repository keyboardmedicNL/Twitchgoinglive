import housey_logging
housey_logging.configure()

import logging
import time
import requests
from os.path import exists
import os
import shutil
import config_loader
import discord_webhook_embeds
import embed_file_handler
import twitch_api_handler
import sys

# vars

logger = logging.getLogger(__name__)

config = config_loader.load_config

discord_webhook_send = discord_webhook_embeds.discord_webhook_send
discord_webhook_edit = discord_webhook_embeds.discord_webhook_edit
discord_webhook_delete = discord_webhook_embeds.discord_webhook_delete
discord_webhook_edit_to_offline = discord_webhook_embeds.discord_webhook_edit_to_offline

save_message_id_to_file = embed_file_handler.save_message_id_to_file
read_message_id_from_file = embed_file_handler.read_message_id_from_file
remove_message_id_file = embed_file_handler.remove_message_id_file

read_twitch_api_token_from_file = twitch_api_handler.read_twitch_api_token_from_file
get_token_from_twitch_api = twitch_api_handler.get_token_from_twitch_api
get_stream_json_from_twitch = twitch_api_handler.get_stream_json_from_twitch

time_before_retry = 60

# functions
def log_exception(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))

# gets list of streamers to poll
def get_streamers_from_file() -> list:
    with open("config/streamers.txt", 'r') as file_with_streamer_ids:
        list_of_streamers = [line.rstrip() for line in file_with_streamer_ids]
        if "http" in list_of_streamers[0]:
            error_count = 0
            while error_count < 4:
                try:
                    get_streamers_trough_request_response = requests.get(list_of_streamers[0])
                    if get_streamers_trough_request_response.ok:
                        list_of_streamers = get_streamers_trough_request_response.text.splitlines()
                        break
                    else:
                        logger.error('was unable to get list of streamers trough request with response: %s with exception: %s waiting for %s seconds', get_streamers_trough_request_response, time_before_retry)
                        error_count = error_count+1
                        time.sleep(time_before_retry)
                except Exception as e:
                    logger.error('was unable to get list of streamers trough request with exception: %s waiting for %s seconds', e, time_before_retry)
                    error_count = error_count+1
                    time.sleep(time_before_retry)
            if error_count == 4:
                raise RuntimeError("tried to get list of streamers trough url 3 times and failed")

    logger.info('list of streamers to poll from: %s', list_of_streamers)

    return(list_of_streamers)

# creates embeds folder if not exist allready
def create_embeds_folder():
    if not exists("config/embeds"):
        os.makedirs("config/embeds")
        logger.info('embed folder was not found so it was created')

def clean_up_old_embeds(list_of_streamers: list ,use_offline_message: bool):
    for streamer in list_of_streamers:
        if exists(f"config/embeds/{streamer}.txt"):
            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
            if use_offline_message:
                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
            else:
                discord_webhook_delete(message_id_from_file)
            remove_message_id_file(streamer)
    logger.info("cleaned up old embeds posted to webhook")
    for filename in os.listdir("config/embeds"):
        file_path = os.path.join("config/embeds", filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    logger.info("removed all remaining files in config/embeds/")

def main():
    sys.excepthook = log_exception

    loaded_config = config()
        
    poll_interval_minutes = loaded_config.poll_interval*60

    create_embeds_folder()
    # gets list of streamers once to clean up old embeds, ends script if it fails to get list of streamers
    token_from_twitch = read_twitch_api_token_from_file()
    
    logger.info("pulling list of streamers once to clean up old messages")
    
    streamers = get_streamers_from_file()
    clean_up_old_embeds(streamers, loaded_config.use_offline_messages)

    # main loop
    while True:
        streamers = get_streamers_from_file()
        for streamer in streamers:
            # gets streamer data from twitch api
            get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer,token_from_twitch)
            # if request to twitch api fails requests a new token from twitch and tries again
            if not get_stream_json_from_twitch_response.ok:
                token_from_twitch = get_token_from_twitch_api()
                get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer,token_from_twitch)
            # checks if streamer is in allowed categories or if allowed categories is empty
            if is_live and (stream_category.lower() in loaded_config.allowed_categories or len(loaded_config.allowed_categories)==0):
                
                if stream_category.lower() in loaded_config.allowed_categories:
                    logger.info('%s for %s with name %s is found in allowed categories: %s', stream_category, streamer, streamer_name, loaded_config.allowed_categories)
                # updates embed if it allready exsists or creates it if not to discord webhook
                if exists(f"config/embeds/{streamer}.txt"):
                    logger.info('embed allready exsists for %s with name %s, updating it',streamer, streamer_name)
                    message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                    discord_webhook_edit(get_stream_json_from_twitch_data,message_id_from_file)
                else:
                    logger.info('no embed exsists for %s with name %s, creating it',streamer, streamer_name)
                    message_id = discord_webhook_send(get_stream_json_from_twitch_data)
                    save_message_id_to_file(streamer,message_id,streamer_name)
            
            else:
                # removes embed if offline or uses offline message
                if exists(f"config/embeds/{streamer}.txt"):
                    logger.info('%s with name %s is no longer live',streamer, streamer_name)
                    message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                    
                    if loaded_config.use_offline_messages:
                        discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
                    else:
                        discord_webhook_delete(message_id_from_file)
                    remove_message_id_file(streamer)
    
        logger.info('finished main loop, waiting for %s minutes',loaded_config.poll_interval)
        time.sleep(poll_interval_minutes)

if __name__ == "__main__":
    main()