from django.test import TestCase
from .models import *
from .serializers import *
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
# Create your tests here.

class UserApiTest(TestCase):
    def setUp(self):
        self.user1 = AuthUser.objects.create(username='tuser1', email="123@126.com")
        self.user1.set_password('123456')
        self.user1.save()

        self.user2 = AuthUser.objects.create(username='tuser2', email="124@126.com", is_active=0)
        self.user2.set_password('123457')
        self.user2.save()

        self.client = APIClient()
        
        self.log_url = '/chat/login/'
        self.register_url = '/chat/register/'

    def test_user_login_success(self):
        response = self.client.post(self.log_url, data={"username": "tuser1", "password": "123456"}, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        
    def test_unregistered_user_login(self):
        response = self.client.post(self.log_url,data={"username":"tuser3","password":"1233456"},format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,{'error':"Invalid User"})
        
    def test_inactive_user_login(self):
        response = self.client.post(self.log_url,data={"username":"tuser2","password":"123457"},format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data,{'error':"Invalid User"})
        
    def test_register_user(self):
        response = self.client.post(self.register_url,data={"username":"yhh","email":"2827883762@qq.com","password":"12321341"},format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        
    def test_register_user_with_existed_username(self):
        response = self.client.post(self.register_url,data={"username":"tuser1","email":"2827883762@qq.com","password":"12321341"},format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        
class ChatApiTest(TestCase):
    def setUp(self):
        self.user1 = AuthUser.objects.create(username='test1',email='123@126.com')
        self.user1.set_password('123456')
        self.user1.save()
        
        self.user2 = AuthUser.objects.create(username='test2',email='124@126.com')
        self.user2.set_password('123457')
        self.user2.save()
        
        self.client1 = APIClient()
        refresh = RefreshToken.for_user(self.user1)
        access_token = str(refresh.access_token)
        self.client1.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        self.client2 = APIClient()
        refresh2 = RefreshToken.for_user(self.user2)
        access_token2 = str(refresh2.access_token)
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token2}')
        
        self.chat_url = '/chat/chat/'
        
    def test_chat_with_qwen(self):
        conversation_id = str(uuid.uuid4())
        data = {
            "content": "你好！你是谁",
            "conversation_id": conversation_id
        }
        response = self.client1.post(self.chat_url, data=data, format="json")

        # 🔹 确保响应状态码是 200 OK（因为 StreamingHttpResponse 默认是 200）
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 🔹 读取流式响应内容
        response_text = ""
        for chunk in response.streaming_content:  # 逐步获取流式返回的数据
            response_text += chunk.decode("utf-8")

        print(f"模型回复: {response_text}")  # 观察 AI 回复内容

        # 🔹 确保数据库中有 AI 生成的消息
        conversation = Conversation.objects.get(id=conversation_id)
        messages = ChatMessages.objects.filter(conversation=conversation)

        self.assertTrue(
            any(msg.role == "assistant" and msg.content == response_text for msg in messages),
            "AI 回复未正确存入数据库"
        )