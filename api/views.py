from django.contrib.auth import authenticate
from .models import User
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer

from .SteamGame import SteamApi
# Create your views here.


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data.get('username')
        # 用户已经存在
        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    return Response({'error': 'Invalid Credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def bindSteamUser(request):
    if request.method == 'POST':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 1}, status=200)
        else:
            return Response(serializer.errors, status=400)
    else:
        return Response({'success': 0, 'error': '请求方法错误'}, status=400)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getUserInfo(request):
    if request.user.is_authenticated:
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    else:
        # 用户未登录，返回相应的错误信息
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getSteamGameInfo(request):
    if request.user.is_authenticated:
        user = request.user
        steamUserName = user.steamUserName
        steamApi = SteamApi()
        gameInfo = steamApi.getOwnedGames(steamUserName)
        return Response(gameInfo, status=200)
    else:
        # 用户未登录，返回相应的错误信息
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
