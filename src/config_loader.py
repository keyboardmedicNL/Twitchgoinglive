import getpass
import yaml
import logging
import sys

default_config = {
    "twitch_api_id":"",
    "twitch_api_secret":"",
    "discord_webhook_url":"",
    "poll_interval":10,
    "allowed_categories":(),
    "message_before_embed":"",
    "use_offline_messages":False
}

# loads config from file
def load_config() -> dict:
    try:
        with open("config/config.yaml") as config_file:
            config_yaml = yaml.safe_load(config_file)
            merged_config = config_object({**default_config, **config_yaml})
        if merged_config.twitch_api_id == "YOUR_API_ID" or merged_config.twitch_api_secret == "YOUR_API_SECRET" or merged_config.discord_webhook_url == "YOUR_WEBHOOK_URL":
            cli_config_builder()
        #raise RuntimeError("you are missing required values in your config. please fill them in and try again")
        else:
            logging.info("succesfully loaded config")        
            return(merged_config)
    except:
        logging.error("unable to find config. starting configurator...")
        cli_config_builder()
    

class config_object:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)

def cli_config_builder():
    config_to_build = {}
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
    cli_api_id = input()
    config_to_build.update({"twitch_api_id": cli_api_id})

    print("please input your twitch api secret :")
    cli_api_secret = getpass.getpass()
    config_to_build.update({"twitch_api_secret": cli_api_secret})

    print("please input your discord webhook url to post the messages to :")
    cli_webhook_url = input()
    config_to_build.update({"discord_webhook_url": cli_webhook_url})

    print("please input interval at wich the script will check if people are live in minutes below or leave blank for the default (10) :")
    cli_interval = input()
    if cli_interval == "":
        cli_interval = 10
    else:
        cli_interval = int(cli_interval)
    config_to_build.update({"poll_interval": cli_interval})

    print("please input all allowed categories seperated by a comma below or leave blank for the default (no category filtering) :")
    cli_categories_string = input()
    if cli_categories_string != "":
        cli_categories = cli_categories_string.split(",")
    else:
        cli_categories = cli_categories_string
    config_to_build.update({"allowed_categories": cli_categories})

    print("please input a custom message to display before the embed of someone being live or leave blank for the default (no custom message) :")
    cli_message = input()
    config_to_build.update({"message_before_embed": cli_message})

    print("please input true or false for wether or not you want to the script to delete embeds from streamers who are offline or display an offline message instead, or leave blank for the default (false) :")
    cli_offline_messages = input()
    if cli_offline_messages.lower == "false" or cli_offline_messages == "":
        cli_offline_messages = False
    else:
        cli_offline_messages = True
    config_to_build.update({"use_offline_messages": cli_offline_messages})

    print("configurator complete... saving to config/config.yaml")
    with open('config/config.yaml', 'w') as file:
        yaml.dump(config_to_build, file)
    
    print("please restart the main script to continue...")
    sys.exit()


if __name__ == "__main__":
    cli_config_builder()