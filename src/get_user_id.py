import twitch_api_handler
import time
import twitch_api_handler

get_streamer_info = twitch_api_handler.get_streamer_info

#functions
def check_if_id_allready_in_streamers_file(user_id: str,) -> bool:
    with open(f"config/streamers.txt", 'r') as streamers_file:
        list_of_streamers = [line.rstrip() for line in streamers_file]

    for streamer in list_of_streamers:
        if user_id == streamer.split()[0]:
            allready_in_file = True
            break
        else:
            allready_in_file = False

    return(allready_in_file)

def main():

    print ("Get twitch user id script by keyboardmedic:")
    time.sleep(1)
    print("you can stop this script at any time by pressing ctrl+c")
    print("------")
    time.sleep(1)

    token = twitch_api_handler.get_token_from_twitch_api()

    while True:
        save_choice = ""
        print("please input the user name you would like to get the id for: ")
        user_name = input()

        response = get_streamer_info(user_name, token)

        responsejson = response.json()
        user_id = responsejson["data"][0]["id"]
        print(f"the user id for {user_name} = {user_id}")

        print("would you like to save the id to your streamers.txt? (Y) or n ")
        save_choice = input() 

        if save_choice.lower() == "y" or save_choice == "":
            if not check_if_id_allready_in_streamers_file(user_id):
                with open(f"config/streamers.txt", 'a') as streamers_file:
                    streamers_file.write(f"\n{user_id}")
                print(f"added new line to streamers.txt: {user_id}")
            else:
                print(f"{user_id} allready exsists in streamers.txt. skipping save...")
            print("------")
        else:
            print("------")

if __name__ == "__main__":
    main()