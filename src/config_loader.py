import yaml

default_config = {
    "twitch_api_id":"",
    "twitch_api_secret":"",
    "discord_webhook_url":"",
    "discord_remote_log_url":"",
    "poll_interval":10,
    "use_discord_logs":False,
    "use_gotify":False,
    "gotify_url":"",
    "ping_id":"",
    "verbose":0,
    "allowed_categories":(),
    "message_before_embed":"",
    "use_offline_messages":False
}

# loads config from file
def load_config() -> dict:
    with open("config/config.yaml") as config_file:
        config_yaml = yaml.safe_load(config_file)
        merged_config = {**default_config, **config_yaml}

    print("succesfully loaded config")

    return(merged_config)