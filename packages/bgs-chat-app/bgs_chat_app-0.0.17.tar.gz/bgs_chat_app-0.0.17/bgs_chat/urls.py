"""
URL configuration for bgs_chat project.
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
print('*'*30)
print('BGS_CHAT_APP/URLS.PY')
print('*'*30)

urlpatterns = [
    path("api/init_conversation", views.init_conversation),
    path("api/send_message", views.send_message),
    path("api/get_response", views.get_messages),
]

# TODO: end_conversation, refresh_token