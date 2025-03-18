import uuid
from time import sleep 
from django.core.cache import cache
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from Qwen2_5 import backend_chat
from .models import *
from .serializers import *


if not cache.get('model_tokenlizer'):
    cache.set("model_tokenizer",backend_chat._load_model_tokenizer(),None)

# Create your views here. 
class ChatViewset(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self,request):
        content = request.data.get('content')
        role = 'user'
        user = request.user
         # 获取conversation_id，并确保是有效的UUID
        conversation_id = request.data.get('conversation_id')
        if conversation_id:
            try:
                # 如果conversation_id有效，尝试获取或创建 Conversation
                conversation_id = uuid.UUID(conversation_id)  # 尝试转换为UUID
                conversation, created = Conversation.objects.get_or_create(
                    id=conversation_id, user=user, title='Test title'
                )
            except ValueError:
                return Response({'error': 'Invalid conversation_id format'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 如果没有提供conversation_id，创建一个新的Conversation
            conversation = Conversation.objects.create(
                user=user, title='Test title'
            )
        msgs = ChatMessages.objects.filter(conversation=conversation)
        serializer = ChatMessagesSerializer(msgs,many=True)
        history = [{"role": msg["role"], "content": msg["content"]} for msg in serializer.data]
        history.append({"role":role,"content":content})
        model, tokenizer = cache.get("model_tokenizer")
        def generate_stream():
            partial_text = ""
            for new_text in backend_chat.get_response_stream(model, tokenizer, history):
                yield new_text  # 立即返回 token
                partial_text += new_text
            # 生成完成后存入数据库
            with transaction.atomic():
                ChatMessages.objects.create(role=role, content=content, conversation=conversation)
                ChatMessages.objects.create(
                    role="assistant", content=partial_text, conversation=conversation
                )

        # serializer = ChatMessagesSerializer(msg)
        return StreamingHttpResponse(generate_stream(), content_type="text/plain")

class RegisterView(APIView):
    def post(self,request):
        try:
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            user =  AuthUser.objects.create(username=username,email = email,password=password)
            return Response({'message':"Register Success"},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error':str(e)},status=status.HTTP_400_BAD_REQUEST)
            
class LoginView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error':"Please provide username or password"},status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(request,username=username,password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            return Response({
                    'access_token': access_token,
                    'refresh_token':str(refresh),
                    'expires_in': refresh.access_token.lifetime.total_seconds(),
                    'is_superuser': user.is_superuser,
                    'is_staff':user.is_staff,
                }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)