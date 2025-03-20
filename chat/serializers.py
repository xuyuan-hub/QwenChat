from rest_framework import serializers
from .models import *

class ChatMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessages
        fields = ['id', 'role', 'content', 'start_time']
        
class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id','title','start_date']
        
class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = ChatMessagesSerializer(many=True,read_only=True,source="conversation")
    class Meta:
        model = Conversation
        fields = ['id','title','start_date','messages']
        
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = AuthUser.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])  # 这里加密密码
        user.save()
        return user