# loads libraries needed in script
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json
import requests

# formats embed for discord webhook and posts to url
def discord_remote_log(title,color,description):
    if use_discord_logs.lower() == "true":
        data_for_log_hook = {"embeds": [
                {
                    "title": title,
                    "color": color,
                    "description": description
                }
            ]}
        rl = requests.post(discord_remote_log_url, json=data_for_log_hook)

# loads config into variables for use in script
with open("config/config.json") as config: # opens config and stores data in variables
    config_json = json.load(config)
    web_server_url = str(config_json["web_server_url"])
    web_server_port = int(config_json["web_server_port"])
    use_discord_logs = str(config_json["use_discord_logs"])
    if use_discord_logs.lower() == "true":
        discord_remote_log_url = str(config_json["discord_remote_log_url"])
    print("<WEBSERVER> Succesfully loaded config")
    discord_remote_log("Goinglivebot/webserver",14081792,"succesfully loaded config")

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
    webServer = HTTPServer((web_server_url, web_server_port), MyServer)
    print("<WEBSERVER> Server started http://%s:%s" % (web_server_url, web_server_port))
    discord_remote_log("Goinglivebot/webserver",703235,"Server started http://%s:%s" % (web_server_url, web_server_port))
    webServer.serve_forever()