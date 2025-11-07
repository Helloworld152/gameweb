import os

import requests
from django.conf import settings


DEFAULT_STEAM_API_KEY = '93829F96E9B5D556148B5F319BC0A9E0'
api_key = getattr(settings, 'STEAM_API_KEY', None) or os.getenv('STEAM_API_KEY') or DEFAULT_STEAM_API_KEY

default_proxy = 'http://127.0.0.1:7890'
http_proxy = os.getenv('HTTP_PROXY', default_proxy)
https_proxy = os.getenv('HTTPS_PROXY', http_proxy or default_proxy)

proxies = {}
if http_proxy:
    proxies['http'] = http_proxy
if https_proxy:
    proxies['https'] = https_proxy

request_timeout = float(os.getenv('STEAM_HTTP_TIMEOUT', '15'))


def _get(url, *, params=None):
    try:
        response = requests.get(url, params=params, proxies=proxies or None, timeout=request_timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise RuntimeError(f'Steam API 请求失败: {exc}') from exc

class SteamGame:
    def __init__(self, username, api_key = api_key):
        self.username = username
        self.api_key = api_key
        self.steam_id = self.getSteamID()

    def getSteamID(self):

        if not self.api_key:
            raise ValueError('STEAM_API_KEY is not configured')

        url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1?key={self.api_key}&vanityurl={self.username}'
        response = _get(url)
        data = response.json()
        return data.get('response', {}).get('steamid')

    def getOwnedGames(self):
        if not self.api_key:
            raise ValueError('STEAM_API_KEY is not configured')

        url = (
            "http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
            f"?key={self.api_key}&steamid={self.steam_id}&include_appinfo=true&include_free_sub=false"
        )
        response = _get(url)
        data = response.json()
        return data.get('response', {}).get('games')

class SteamApi:
    def __init__(self):
        self.api_key = api_key

    def getSteamID(self, username):
        url = f'http://api.steampowered.com/ISteamUser/ResolveVanityURL/v1?key={self.api_key}&vanityurl={username}'
        response = _get(url)
        data = response.json()
        return data.get('response', {}).get('steamid')

    def getOwnedGames(self, username):
        if not self.api_key:
            raise ValueError('STEAM_API_KEY is not configured')

        steam_id = self.getSteamID(username)
        if steam_id:
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={self.api_key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true"

            response = _get(url)
            data = response.json()
            return data.get('response', {}).get('games')

    def getDiscountedGames(self):
        if not self.api_key:
            raise ValueError('STEAM_API_KEY is not configured')

        url = "https://store.steampowered.com/api/featuredcategories"
        params = {
            'key': self.api_key
        }
        response = _get(url, params=params)
        data = response.json()
        return data.get("Specials")

