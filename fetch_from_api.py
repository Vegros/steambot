import requests
from dotenv import load_dotenv
import os
import json
import re

class Api:
    load_dotenv()

    def __init__(self, game_name):
        self.game = str(game_name).lower().replace(' ', '_')

    def return_games_found(self):
        try:
            with open('game_list.json', 'r') as json_file:
                data = json.load(json_file)

            games_found = []
            count = 0
            for game in data.get("apps", []):
                if self.game in game.get("name", ""):
                    found = {"id": count, "game_name": game.get("name"), "appid": game.get("appid")}
                    count += 1
                    games_found.append(found)

            return games_found
        except Exception as e:
            self.fetch_games()
            return {}


    def check_for_game(self):
        try:
            games_found = self.return_games_found()

            for game in games_found:
                print( str(game.get("id") )+ ": " + game.get('game_name'))
            if games_found:
                choice = int(input("Choose the game you wanted: "))

                for game in games_found:
                    if game.get("id") == choice:
                        self.game_name = game.get("game_name")
                        return game.get("appid")

            return ""
        except Exception as e:
            print(e)
            return ""



    def fetch_games(self):
            print("fetching from api")
            url = os.getenv("fetch_games_url")
            get_response = requests.get(url=url, timeout=10)
            format_response = get_response.json().get("applist", [])
            response = {'apps': []}
            for game in format_response.get('apps', []):
                name = str(game.get("name")).lower().replace('™', ' ').replace(' ', '_').replace(':','-')
                new_game = {'appid': game.get("appid"), "name": name}
                response.get("apps").append(new_game)

            with open('game_list.json', 'w') as json_file:
                json.dump(response, json_file, indent=4)

    def fetch_game_api(self, appid, game_name):
        if appid:
            url = os.getenv('game_url') + "" + str(appid)
            print(url)
            get_response = requests.get(url=url, timeout=10)
            format_response = get_response.json().get(f"{appid}", {}).get("data", {})
            file_name = game_name + ".json"

            with open(file_name, 'w') as json_file:
                json.dump(format_response, json_file, indent=4)

            return True
        return False
