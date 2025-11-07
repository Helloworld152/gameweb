from django.contrib.auth import authenticate
from .models import User, Post, Comment
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, PostSerializer, CommentSerializer

from .SteamGame import SteamApi
# Create your views here.
@api_view(['GET'])
def test(request):
    return Response({'success': 1}, 200)

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
        steam_username = request.data.get('steamUserName', '').strip()
        if not steam_username:
            return Response({'error': 'steamUserName 必填'}, status=400)
        serializer = UserSerializer(request.user, data={'steamUserName': steam_username}, partial=True)
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
        if not steamUserName:
            return Response({'error': 'Steam 用户名未绑定'}, status=400)
        try:
            gameInfo = steamApi.getOwnedGames(steamUserName)
        except (ValueError, RuntimeError) as exc:
            return Response({'error': str(exc)}, status=502)

        if gameInfo is None:
            return Response({'error': '无法获取 Steam 游戏数据'}, status=502)

        return Response(gameInfo, status=200)
    else:
        # 用户未登录，返回相应的错误信息
        return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def getSteamDiscounts(request):
    steamApi = SteamApi()
    try:
        deals = steamApi.getDiscountedGames()
    except (ValueError, RuntimeError) as exc:
        return Response({'error': str(exc)}, status=502)

    return Response(deals or [], status=200)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def unbindSteamUser(request):
    if request.method == 'GET':
        user = request.user
        user.steamUserName = None
        user.save()
        return Response({'success': 1}, status=200)
    else:
        return Response({'success': 0, 'error': '请求方法错误'}, status=400)


# 帖子相关功能
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createPost(request):
    title = request.data.get('title', '').strip()
    content = request.data.get('content', '').strip()

    if not title:
        return Response({'error': '标题不能为空'}, status=400)
    if not content:
        return Response({'error': '内容不能为空'}, status=400)

    post = Post.objects.create(title=title, content=content, author=request.user)
    serializer = PostSerializer(post)
    return Response(serializer.data, status=201)

@api_view(['GET'])
def getAllPosts(request):
    posts = Post.objects.order_by('-create_time')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getMyPosts(request):
    user = request.user
    posts = Post.objects.filter(author=user).order_by('-create_time')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def postDetail(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({"error": "Post not found"}, status=404)

    if request.method == 'GET':
        serializer = PostSerializer(post)
        return Response(serializer.data, status=200)

    if post.author_id != request.user.id and not request.user.is_staff:
        return Response({'error': '没有权限删除此帖子'}, status=403)

    post.delete()
    return Response(status=204)


# 评论功能
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def postComments(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    if request.method == 'GET':
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        content = request.data.get('content', '').strip()
        if not content:
            return Response({'error': '评论内容不能为空'}, status=400)
        user = request.user
        comment = Comment.objects.create(post=post, content=content, author_id=user.id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=201)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deleteComment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found"}, status=404)

    if comment.author_id != request.user.id and not request.user.is_staff:
        return Response({'error': '没有权限删除此评论'}, status=403)

    comment.delete()
    return Response(status=204)
