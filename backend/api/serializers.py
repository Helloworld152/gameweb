from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    steamUserName = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'steamUserName')
        extra_kwargs = {'password':{'write_only': True}}

    def create(self, validated_data):
        steamUserName = validated_data.pop('steamUserName', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        if steamUserName:
            user.steamUserName = steamUserName
            user.save()

        return user


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_username', 'create_time']


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'content', 'create_time']
