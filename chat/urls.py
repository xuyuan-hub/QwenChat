from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as rest_views

router= DefaultRouter()
router.register(r'chat', ChatViewset, basename='chat')  # 自动注册 chat/ 和 chat/<id>/

app_name = "chat"
urlpatterns = [
    path("", include(router.urls)),
    path("login/",LoginView.as_view(),name='login'),
    path("register/",RegisterView.as_view(),name='register')
]

urlpatterns += router.urls