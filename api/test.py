# import SteamGame
#
# steam = SteamGame.SteamApi()
# print(steam.getDiscountedGames())
# print(steam.getSteamID('techtalkapples'))
# print(steam.getOwnedGames('techtalkapples'))

import requests
from bs4 import BeautifulSoup

api_key = '93829F96E9B5D556148B5F319BC0A9E0'

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/85.0.4183.102 Safari/537.36', 'Accept-Language': 'zh-CN '
}

def get_discounted_games():
    url = "https://store.steampowered.com/search/?specials=1&page=1&os=win"
    response = requests.get(url, proxies=proxies, headers=headers)
    print(response.content)
    soup = BeautifulSoup(response.content, "html.parser")

    games = soup.find_all('a', class_='search_result_row')

    for game in games:
        title = game.find('span', class_='title').text
        discount = game.find('div', class_='search_discount').text.strip()
        original_price = game.find('strike').text if game.find('strike') else None
        discounted_price = game.find('div', class_='search_price').text.strip().split('$')[-1]

        print(f"Title: {title}")
        print(f"Discount: {discount}")
        print(f"Original Price: {original_price}")
        print(f"Discounted Price: ${discounted_price}")
        print("")

if __name__ == "__main__":
    get_discounted_games()
