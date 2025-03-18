from django.urls import path,include
from .views import *
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as rest_views

router= DefaultRouter()

app_name = "chat"
urlpatterns = [
    path("chat/",ChatViewset.as_view(),name='chat'),
    path("login/",LoginView.as_view(),name='login'),
    path("register/",RegisterView.as_view(),name='register')
]

urlpatterns += router.urls