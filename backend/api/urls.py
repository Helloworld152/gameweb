from django.urls import path
from .views import *

urlpatterns = [
    path('test/', test, name='test'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('bindsteam/', bindSteamUser, name='bindSteam'),
    path('unbindsteam/', unbindSteamUser, name='unbindsteam'),
    path('userinfo/', getUserInfo, name='getUserInfo'),
    path('steamgameinfo/', getSteamGameInfo, name='getSteamGameInfo'),
    path('myposts/', getMyPosts, name='getMyPosts'),
    path('allposts/', getAllPosts, name='getAllPosts'),
    path('newpost/', createPost, name='createPost'),
    path('posts/<int:post_id>/', postDetail, name='postDetail'),
    path('posts/<int:post_id>/comments/', postComments, name='postComments'),
    path('comments/<int:comment_id>/', deleteComment, name='deleteComment')
]