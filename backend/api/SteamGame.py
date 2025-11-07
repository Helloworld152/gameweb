import requests
from django.conf import settings


STEAM_API_KEY = '93829F96E9B5D556148B5F319BC0A9E0'
STEAM_REGION = 'cn'
STEAM_LANGUAGE = 'schinese'
HTTP_PROXY = 'http://127.0.0.1:7890'
REQUEST_TIMEOUT = 15

api_key = getattr(settings, 'STEAM_API_KEY', None) or STEAM_API_KEY

proxies = {
    'http': HTTP_PROXY,
    'https': HTTP_PROXY
}


def _get(url, *, params=None):
    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=REQUEST_TIMEOUT)
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
            'key': self.api_key,
            'cc': STEAM_REGION,
            'l': STEAM_LANGUAGE
        }
        response = _get(url, params=params)
        data = response.json()
        specials = data.get("Specials", {})
        items = specials.get('items') or specials.get('large_capsules') or []
        deals = []
        for item in items:
            deals.append({
                'appid': item.get('id') or item.get('appid'),
                'name': item.get('name'),
                'discount_percent': item.get('discount_percent'),
                'original_price': item.get('original_price'),
                'final_price': item.get('final_price'),
                'header_image': item.get('large_capsule') or item.get('small_capsule') or item.get('header'),
                'capsule_image': item.get('small_capsule'),
                'url': item.get('url'),
                'reviews_summary': item.get('reviews_summary'),
                'platform_icons': item.get('platform_icons'),
                'tags': item.get('tags')
            })
        return [deal for deal in deals if deal['name']][:40]

