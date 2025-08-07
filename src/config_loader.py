import getpass
import yaml
import logging
import time

default_config = {
    "twitch_api_id":"",
    "twitch_api_secret":"",
    "discord_webhook_url":"",
    "discord_remote_log_url":"",
    "poll_interval":10,
    "allowed_categories":(),
    "message_before_embed":"",
    "use_offline_messages":False
}

# loads config from file
def load_config() -> tuple[dict, str]:
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)
        merged_config = config_object({**default_config, **config_yaml})
    
    if merged_config.twitch_api_id == "YOUR_API_ID" or merged_config.twitch_api_secret == "YOUR_API_SECRET" or merged_config.discord_webhook_url == "YOUR_WEBHOOK_URL":
        cli_config_builder()
        #raise RuntimeError("you are missing required values in your config. please fill them in and try again")
    else:
        logging.info("succesfully loaded config")
    
    return(merged_config)

class config_object:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)

def cli_config_builder():
    print("starting configurator for twitchgoinglive...")
    print("------")
    print("it appears your config does not contain all required values to run twitchgoinglive")
    print("this configurator will allow you to enter the values here in the command line and save them to the config")
    print("------")
    print("you can press ctrl+c at any time to exit this configurator")
    print("if you want to run this configurator again in the future you can run the corresponding configurator.bat/sh for your operating system")
    print("")
    print("")
    print("please input your twitch api id :")
    twitch_api_id = input()
    print("please input your twitch api secret :")
    twitch_api_secret = getpass.getpass()
    print("please input your discord webhook url to post the messages to :")
    discord_webhook_url = input()
    print("please input interval at wich the script will check if people are live in minutes below or leave blank for the default (10) :")
    poll_interval = input()
    if poll_interval == "":
        poll_interval = 10
    else:
        poll_interval = int(poll_interval)
    print("please input all allowed categories seperated by a comma below or leave blank for the default (no category filtering) :")
    allowed_categories_string = input()
    if allowed_categories_string == "":
        allowed_categories = ()
    else:
        allowed_categories = allowed_categories_string.split(",")
    print("please input a custom message to display before the embed of someone being live or leave blank for the default (no custom message) :")
    custom_message = input()
    print("please input true or false for wether or not you want to the script to delete embeds from streamers who are offline or display an offline message instead, or leave blank for the default (false) :")
    use_offline_messages = input()
    if use_offline_messages.lower == "false" or use_offline_messages == "":
        use_offline_messages = False
    else:
        use_offline_messages = True
    print("configurator complete... saving to config/config.yaml and starting script")
    print("if you started this script trough docker you can press ctrl+p followed by ctrl+q to detach from this shell and continue running the script")
    print("waiting for 10 seconds before starting main script")
    time.sleep(10)

if __name__ == "__main__":
    cli_config_builder()