# loads libraries needed in script
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests

#variables used in script
configcheck=False

# formats embed for discord webhook and posts to url
def discordremotelog(title,color,description):
    if webhooklogurl != "":
        data = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(webhooklogurl, json=data)

# loads config into variables for use in script
while configcheck == False: # loop to ensure config gets loaded
    try:
        with open("config/config.json") as config: # opens config and stores data in variables
            configJson = json.load(config)
            hostName = configJson["hostname"]
            serverPort = int(configJson["webport"])
            webhooklogurl = configJson["webhooklogurl"]
            config.close()
            configcheck = True # stops loop if succesfull
            print("<WEBSERVER> Succesfully loaded config")
            discordremotelog("Goinglivebot/webserver",14081792,"succesfully loaded config")
    except Exception as e: # catches exception
        print(f"An exception occurred whilst trying to read the config: {str(e)} waiting for 1 minute")

        time.sleep(60)

# start webserver
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>Hello, i am a webserver.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("<WEBSERVER> Server started http://%s:%s" % (hostName, serverPort))
    discordremotelog("Goinglivebot/webserver",703235,"Server started http://%s:%s" % (hostName, serverPort))


    webServer.serve_forever()