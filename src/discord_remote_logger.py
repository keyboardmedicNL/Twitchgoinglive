import config_loader
import time
import requests
import logging

loaded_config = config_loader.load_config()


# simple discord webhook send for remote logging
def discord_remote_log(title: str ,color: str ,description: str ,ping: bool): 
    if loaded_config.use_discord_logs:
        try:
            if color.lower() == "blue":
                color = 1523940
            elif color.lower() == "yellow":
                color = 14081792
            elif color.lower() == "red":
                color = 10159108
            elif color.lower() == "green":
                color = 703235
            elif color.lower() == "purple":
                color = 10622948
            elif color.lower() == "gray" or color.lower() == "grey":
                color = 1776669
            
            if ping:
                ping_string = f"<@{loaded_config.ping_id}>"
            else:
                ping_string = ""
            
            data_for_log_hook = {"content": ping_string, "embeds": [
                    {
                        "title": title,
                        "color": color,
                        "description": description
                    }
                ]}
            
            remote_log_send_request_to_discord = requests.post(loaded_config.discord_remote_log_url, json=data_for_log_hook, params={'wait': 'true'})
            logging.debug('sending message to discord remote log webhook with title: %s color: %s description: %s and ping %s . Discord response is: %s',title, color, description, ping_string, str(remote_log_send_request_to_discord))
            
            time.sleep(1)
        except Exception as e:
            logging.error("unable to send discord log message with exception: %s", e)