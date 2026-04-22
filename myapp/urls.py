#my app urls

"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from .views import get_users_with_unread

urlpatterns = [
    path('', views.signup_desh, name='signup_desh'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('signup_desh/', views.signup_desh, name='signup_desh'),
    path('home/', views.home, name='home'),
    path('chat/', views.chat, name='chat'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('get-messages/<int:user_id>/', views.get_messages, name='get_messages'),
    path('send-message/', views.send_message, name='send_message'),
    path('show_logs/', views.show_logs, name='show_logs'),
    path('get_users_with_unread/', views.get_users_with_unread, name='get_users_with_unread'),
    path('users-with-unread/', get_users_with_unread, name='users_with_unread'),
]