import logging
import re

def sanitize_streamer_username(name: str, list_of_names_to_handle: str, use_skybass: bool, replacement: str="") -> str:

    if use_skybass:
        for name_to_handle in list_of_names_to_handle:
            if name != name_to_handle["name"]:

                sanitized = re.sub(r'[_-]*(dj|dnb|music|vox)[_-]*', replacement, name,  flags=re.I)

                sanitized.replace("-"," ")
                sanitized.replace("_"," ")

                logging.debug("replaced name %s with %s", name, sanitized)

                return sanitized
            try:
                logging.debug("name was found in list to ignore and replace_with was used instead, name was: %s and is now: %s", name, name_to_handle["replace_with"])
                return name_to_handle["replace_with"]
            except KeyError:
                return(name)
    else:
        return(name)

def per_streamer_message(name: str, list_of_streamers: list, message: str, game: str) -> str:

    for streamer in list_of_streamers:

        if name.lower() == str(streamer["name"]).lower():

            for category in streamer["categories"]:
                if str(category["name"]).lower() == game.lower():
                    return(category["message"])
            
            return(streamer["message"])
        
    else:
        return(message)
