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

# loads config from file
def load_config() -> dict:
    shoutouts = []
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)

    for per_config in config_yaml["shoutouts"]:
        merged_per_config = per_discord_config | per_config
        shoutouts.append(merged_per_config)

    merged_config = config_object({**default_config, **config_yaml})
    del merged_config.shoutouts

    logging.debug("succesfully loaded config")       
    return(merged_config, shoutouts)


class config_object:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)
