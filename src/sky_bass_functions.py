import logging
import re

def sanitize_streamer_username(name: str, list_of_names_to_ignore: str, replacement: str="") -> str:

    for name_to_ignore in list_of_names_to_ignore:
        if name != name_to_ignore["name"]:

            sanitized = re.sub(r'[_-]*(dj|dnb|music|vox)[_-]*', replacement, name,  flags=re.I)

            sanitized.replace("-"," ")
            sanitized.replace("_"," ")

            logging.debug("replaced name %s with %s", name, sanitized)

            return sanitized
    
    else:
        logging.debug("name was found in list to ignore and replace_with was used instead, name was: %s and is now: %s", name, name_to_ignore["replace_with"])
        return name_to_ignore["replace_with"]

