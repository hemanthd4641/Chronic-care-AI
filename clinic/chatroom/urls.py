from django.urls import path
from . import views
app_name = 'chatroom'
urlpatterns = [
    path('',views.view_chatroom,name='index'),
    path('report/',views.add_new_report,name='report'),
    path('recived/<int:pk>',views.recived_report,name='recived')
]
