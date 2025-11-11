from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("private/", views.private_messages, name="private_messages"),
    path("send/", views.send_private_message, name="send_message"),
    path("message/<int:message_id>/", views.view_message, name="view_message"),
    path("doctor-messages/", views.doctor_patient_messages, name="doctor_patient_messages"),
    path("chat/", views.chat_room, name="chat_room"),
    path("api/send-chat/", views.send_chat_message, name="send_chat_message"),
    path("api/get-messages/", views.get_chat_messages, name="get_chat_messages"),
]

