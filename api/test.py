import SteamGame

steam = SteamGame.SteamApi()
print(steam.getDiscountedGames())
print(steam.getSteamID('techtalkapples'))
print(steam.getOwnedGames('techtalkapples'))