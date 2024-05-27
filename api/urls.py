from django.urls import path
from .views import register, login, bindSteamUser, getUserInfo, getSteamGameInfo

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('bindsteam/', bindSteamUser, name='bindSteam'),
    path('userinfo/', getUserInfo, name='getUserInfo'),
    path('steamgameinfo/', getSteamGameInfo, name='getSteamGameInfo')
]