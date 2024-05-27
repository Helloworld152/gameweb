import requests

api_key = '93829F96E9B5D556148B5F319BC0A9E0'
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'https://127.0.0.1:7890',

}

class SteamGame:
    def __init__(self, username, api_key = api_key):
        self.username = username
        self.api_key = api_key
        self.steam_id = self.getSteamID()

    def getSteamID(self):

        url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1?key={self.api_key}&vanityurl={self.username}'
        try:
            response = requests.get(url, proxies=proxies)
            print(response)
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'steamid' in data['response']:
                    return data['response']['steamid']
                else:
                    return None
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

    def getOwnedGames(self):
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.api_key}&steamid={self.steam_id}&include_appinfo=true&include_free_sub=false"

        try:
            response = requests.get(url)
            print(response)
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'games' in data['response']:
                    return data['response']['games']
                else:
                    return None
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

class SteamApi:
    def __init__(self):
        self.api_key = api_key

    def getSteamID(self, username):
        url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1?key={self.api_key}&vanityurl={username}'
        try:
            response = requests.get(url, proxies=proxies)
            if response.status_code == 200:
                data = response.json()
                if 'response' in data and 'steamid' in data['response']:
                    return data['response']['steamid']
                else:
                    return None
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

    def getOwnedGames(self, username):
        steam_id = self.getSteamID(username)
        if steam_id:
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.api_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true"

            try:
                response = requests.get(url, proxies=proxies)
                if response.status_code == 200:
                    data = response.json()
                    if 'response' in data and 'games' in data['response']:
                        return data['response']['games']
                    else:
                        return None
            except requests.exceptions.RequestException as e:
                print(f'Error: {e}')
                return None

    def getDiscountedGames(self):
        url = "https://store.steampowered.com/api/featuredcategories"
        params = {
            'key': self.api_key
        }
        try:
            response = requests.get(url, params=params, proxies=proxies)
            data = response.json()
            if "Specials" in data:
                specials = data["Specials"]
                return specials

        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')
            return None

