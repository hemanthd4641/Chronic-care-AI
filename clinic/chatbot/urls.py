from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_home, name='chatbot_home'),
    path('ask/', views.ask_bot, name='ask_bot'),
    path('agent-action/', views.ai_agent_action, name='ai_agent_action'),
]
