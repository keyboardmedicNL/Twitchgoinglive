import config_loader
import time
import requests

# vars
loaded_config = config_loader.load_config()

def send_gotify_notification(title: str ,message: str ,priority: str):
    if loaded_config["use_gotify"]:
        requests.post(loaded_config["gotify_url"], data={"title": title, "message": message, "priority":priority})

        if loaded_config["verbose"] >= 2:
            print(f"sending notification to gotify with title: {title} message: {message} priority: {priority}")

        time.sleep(1)