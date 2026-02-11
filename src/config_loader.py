import yaml
import logging

default_config = {
    "twitch_api_id":"YOUR_API_ID",
    "twitch_api_secret":"YOUR_API_SECRET",
    "poll_interval":10,
    "time_before_retry":60,
    "max_errors_allowed":3,
    "allow_failure": False
}

per_discord_config = {
    "discord_webhook_url":"YOUR_WEBHOOK_URL",
    "streamers":[],
    "allowed_categories":[],
    "message_before_embed":"",
    "use_offline_messages":False,
    "team_name": "",
    "excluded_uids":[],
    "use_skybass": False,
    "names_to_ignore": [{
        "name":"name",
        "replace_with":"nothing"
        }],
    "leave_messages_untouched": False
}

old_config = {
    "twitch_api_id":"YOUR_API_ID",
    "twitch_api_secret":"YOUR_API_SECRET",
    "poll_interval":10,
    "time_before_retry":60,
    "max_errors_allowed":3,
    "allow_failure": False,
    "discord_webhook_url":"YOUR_WEBHOOK_URL",
    "allowed_categories":[],
    "message_before_embed":"",
    "use_offline_messages":False,
    "team_name": "",
    "excluded_uids":[],
    "use_skybass": False,
    "names_to_ignore": [{
        "name":"name",
        "replace_with":"nothing"
        }],
    "leave_messages_untouched": False
}

default_keys = ["twitch_api_id","twitch_api_secret","poll_interval","time_before_retry","max_errors_allowed","allow_failure"]

shoutout_keys = ["discord_webhook_url",
    "streamers",
    "allowed_categories",
    "message_before_embed",
    "use_offline_messages",
    "team_name",
    "excluded_uids",
    "use_skybass",
    "names_to_ignore",
    "leave_messages_untouched"]

# loads config from file
def load_config() -> tuple[object,dict]:
    shoutouts = []
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)
    try:
        for per_config in config_yaml["shoutouts"]:
            merged_per_config = per_discord_config | per_config
            shoutouts.append(merged_per_config)

        merged_config = config_object({**default_config, **config_yaml})
        del merged_config.shoutouts

        logging.debug("succesfully loaded config")       
        return(merged_config, shoutouts)

    except KeyError:
        convert_config(config_yaml)


class config_object:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)

def convert_config(config_yaml: dict):
    new_config = {}
    new_shoutout_entry = {}
    old_default_config = create_dict_from_keylist(config_yaml, default_keys)
    old_shoutout_entry = create_dict_from_keylist(config_yaml, shoutout_keys)
    list_of_streamers = streamers_file_to_list()

    old_shoutout_entry.update({"streamers":list_of_streamers})
    new_shoutout_entry.update({"shoutouts":[old_shoutout_entry]})

    new_config = old_default_config | new_shoutout_entry

    print(old_default_config)

def create_dict_from_keylist(config_dict: dict, list_of_keys: list) -> dict:
    created_dict = {}

    for key in list_of_keys:
        try:
            entry = config_dict.get(key)
            if entry:
                created_dict.update({key:entry})
        except KeyError:
            pass

    return(created_dict)

def streamers_file_to_list() -> list:
    with open("config/streamers.txt") as streamers_file:
        return(streamers_file.read().splitlines())
