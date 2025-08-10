import config_loader
import os
import logging

# vars
loaded_config = config_loader.load_config()

def save_message_id_to_file(name: str ,message_id: str ,user_login: str, embed_color: str, user_name: str):
    with open(f"config/embeds/{name}.txt", 'w') as file_to_save_message_id_to:
        file_to_save_message_id_to.write(message_id + '\n' + user_login + '\n' + embed_color + '\n' + user_name)

    logging.debug("message id: %s and name: %s and color: %s and username: %s saved in file %s.txt",message_id, user_login, embed_color, user_name, name)

def read_message_id_from_file(name: str) -> tuple[str, str, str, str]:
    with open(f"config/embeds/{name}.txt", 'r') as file_to_read_from:
        discord_webhook_message_id = str(file_to_read_from.readline())
        discord_webhook_message_id = discord_webhook_message_id.strip("\n")
        name_in_file = str(file_to_read_from.readline())
        name_in_file = name_in_file.strip("\n")
        embed_color = str(file_to_read_from.readline())
        embed_color = embed_color.strip("\n")
        user_name = str(file_to_read_from.readline())

    logging.debug("message id : %s and name: %s and color: %s and username: %s read from %s.txt",discord_webhook_message_id, name_in_file, embed_color, user_name, name)

    return(discord_webhook_message_id, name_in_file, embed_color, user_name)

def remove_message_id_file(name: str):
    os.remove(f"config/embeds/{name}.txt")

    logging.debug("removed file containing message id for embed for %s.txt",name)
