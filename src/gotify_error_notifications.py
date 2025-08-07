import config_loader
import time
import requests
import logging

loaded_config = config_loader.load_config()

def send_gotify_notification(title: str ,message: str ,priority: str):
    if loaded_config.use_gotify:
        requests.post(loaded_config.gotify_url, data={"title": title, "message": message, "priority":priority})

        logging.debug("sending notification to gotify with title: %s message: %s priority: %s",title, message, priority)

        time.sleep(1)