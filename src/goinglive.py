import housey_logging
housey_logging.configure()

import logging
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
import twitch_api_handler
import sys

# vars


logger = logging.getLogger(__name__)

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

read_twitch_api_token_from_file = twitch_api_handler.read_twitch_api_token_from_file
get_token_from_twitch_api = twitch_api_handler.get_token_from_twitch_api
get_stream_json_from_twitch = twitch_api_handler.get_stream_json_from_twitch

# functions
def log_exception(type, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))

# gets list of streamers to poll
def get_streamers_from_file() -> tuple[list, bool]:
    with open("config/streamers.txt", 'r') as file_with_streamer_ids:
        list_of_streamers = [line.rstrip() for line in file_with_streamer_ids]
        if "http" in list_of_streamers[0]:
            get_streamers_trough_request_response = requests.get(list_of_streamers[0])

            if not get_streamers_trough_request_response.ok:
                logger.error('was unable to get list of streamers trough request with response: %s', get_streamers_trough_request_response)
                discord_remote_log("Goinglivebot","red",f"was unable to get list of streamers trough request with response: {get_streamers_trough_request_response}",False)
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
            else:
                list_of_streamers = get_streamers_trough_request_response.text.splitlines()
                is_get_streamers_from_file_succesfull = get_streamers_trough_request_response.ok
        else:
            is_get_streamers_from_file_succesfull = True

    logger.info('list of streamers to poll from: %s', list_of_streamers)
    discord_remote_log("Goinglivebot","yellow",f"list of streamers to poll from: {list_of_streamers}",False)

    return(list_of_streamers, is_get_streamers_from_file_succesfull)

# creates embeds folder if not exist allready
def create_embeds_folder():
    if not exists("config/embeds"):
        os.makedirs("config/embeds")
        logger.info('embed folder was not found so it was created')
        discord_remote_log("Goinglivebot","blue","embed folder was not found so it was created",False)

def clean_up_old_embeds(list_of_streamers: list ,use_offline_message: bool):
    logger.info("pulling list of streamers once to clean up old messages")
    discord_remote_log("Goinglivebot","yellow","pulling list of streamers once to clean up old messages",False)
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
    discord_remote_log("Goinglivebot","blue","cleaned up old embeds posted to webhook and cleaned embeds folder",False)

def main():
    sys.excepthook = log_exception

    loaded_config = config()
    poll_interval_minutes = loaded_config["poll_interval"]*60

    create_embeds_folder()
    # gets list of streamers once to clean up old embeds, ends script if it fails to get list of streamers
    token_from_twitch = read_twitch_api_token_from_file()
    streamers, streamer_get_was_succesfull = get_streamers_from_file()
    if streamer_get_was_succesfull:
        clean_up_old_embeds(streamers, loaded_config["use_offline_messages"])

        # main loop
        while True:
            #try:
            streamers, streamer_get_was_succesfull = get_streamers_from_file()
            if streamer_get_was_succesfull:
                for streamer in streamers:
                    # sets streamer name incase an exception is called before streamer_name is set with a function
                    streamer_name = "unknown"
                    # gets streamer data from twitch api
                    get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer,token_from_twitch)
                    # if request to twitch api fails requests a new token from twitch and tries again
                    if not get_stream_json_from_twitch_response.ok:
                        token_from_twitch = get_token_from_twitch_api()
                        get_stream_json_from_twitch_response,get_stream_json_from_twitch_data,is_live,stream_category,streamer_name = get_stream_json_from_twitch(streamer,token_from_twitch)
                    # checks if streamer is in allowed categories or if allowed categories is empty
                    if is_live and (stream_category.lower() in loaded_config["allowed_categories"] or len(loaded_config["allowed_categories"])==0):
                        
                        if stream_category.lower() in loaded_config["allowed_categories"]:
                            logger.info('%s for %s with name %s is found in allowed categories: %s', stream_category, streamer, streamer_name, loaded_config["allowed_categories"])
                            discord_remote_log("Goinglivebot","green",f"{stream_category} for {streamer} with name {streamer_name} is found in allowed categories",False)
                        # updates embed if it allready exsists or creates it if not to discord webhook
                        if exists(f"config/embeds/{streamer}.txt"):
                            logger.info('embed allready exsists for %s with name %s, updating it',streamer, streamer_name)
                            discord_remote_log("Goinglivebot","yellow",f"embed allready exsists for {streamer} with name {streamer_name}, updating it",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            discord_webhook_edit(get_stream_json_from_twitch_data,message_id_from_file)
                        else:
                            logger.info('no embed exsists for %s with name %s, creating it',streamer, streamer_name)
                            discord_remote_log("Goinglivebot","yellow",f"no embed exsists for {streamer} with name {streamer_name}, creating it",False)
                            message_id = discord_webhook_send(get_stream_json_from_twitch_data)
                            save_message_id_to_file(streamer,message_id,streamer_name)
                    
                    else:
                        # removes embed if offline or uses offline message
                        if exists(f"config/embeds/{streamer}.txt"):
                            logger.info('%s with name %s is no longer live',streamer, streamer_name)
                            discord_remote_log("Goinglivebot","yellow",f"{streamer} with name {streamer_name} is no longer live",False)
                            message_id_from_file,name_from_file = read_message_id_from_file(streamer)
                            
                            if loaded_config["use_offline_messages"]:
                                discord_webhook_edit_to_offline(message_id_from_file,name_from_file)
                            else:
                                discord_webhook_delete(message_id_from_file)
                            remove_message_id_file(streamer)
        
            #except Exception as e:
                #print(f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}")
                #discord_remote_log("Goinglivebot","red",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}",True)
                #send_gotify_notification("Clipbot",f"An exception occurred for streamer {streamer} with name {streamer_name} : {str(e)}","5")
            
            logger.info('finished main loop, waiting for %s minutes',loaded_config["poll_interval"])
            discord_remote_log("Goinglivebot","gray",f"finished main loop, waiting for {loaded_config["poll_interval"]} minutes",False)
            time.sleep(poll_interval_minutes)
    else:
        logger.error("unable to get streamers from file, stopping script....")

if __name__ == "__main__":
    main()