from rest_framework import serializers
from .models import User, Post

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
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'create_time']